#include "Converter.hpp"
#include "MultilinePrinter.hpp"
#include <boost/asio.hpp>
#include <boost/program_options.hpp>
#include <format>
#include <iostream>
#include <ranges>
#include <thread>

namespace po = boost::program_options;

namespace {
void processFile(fs::path filename, LineStreamPtr out) {
  FFmpegRunner fmpr(filename,
                    [out](const std::string &str) { out->print(str); });
  fmpr.run();
}

fs::path getWorkingDirectory(const std::string &opt) {
  if (opt.empty()) {
    return fs::current_path();
  }

  fs::path inputPath(opt);

  if (inputPath.is_absolute()) {
    return inputPath;
  } else {
    return fs::current_path() / inputPath;
  }
}

const std::vector<std::string> ext_whitelist = {".mp4", ".mov", ".mkv",
                                                ".png", ".jpg", ".jpeg"};

void getWhitelistedFiles(const fs::path &root, std::vector<fs::path> &out) {
  if (!fs::exists(root) || !fs::is_directory(root))
    return;

  auto rng = boost::iterator_range<fs::directory_iterator>(
      fs::directory_iterator(root), fs::directory_iterator());

  std::ranges::for_each(
      rng | std::views::filter(
                [](const auto &entry) { return fs::is_directory(entry); }),
      [&out](const auto &entry) { getWhitelistedFiles(fs::path(entry), out); });

  rng = boost::iterator_range<fs::directory_iterator>(
      fs::directory_iterator(root), fs::directory_iterator());

  std::ranges::for_each(rng | std::views::filter([](const auto &entry) {
                          return std::ranges::find(
                                     ext_whitelist,
                                     fs::path(entry).extension().string()) !=
                                 ext_whitelist.end();
                        }),
                        [&out](const auto &entry) { out.push_back(entry); });
}
} // namespace

int main(int argc, char *argv[]) {
  setlocale(LC_ALL, "Russian");

  fs::path workingDir;
  int threads = 4;
  try {
    po::options_description desc("Options");
    desc.add_options()("help,h", "Show this message")(
        "threads,t", po::value<int>()->default_value(4),
        "concurrent ffmpeg instances (4 by default)")(
        "folder", po::value<std::string>(),
        "path to target directory (./ by default)");
    ;

    po::positional_options_description pos_desc;
    pos_desc.add("folder", 1);

    po::variables_map vm;
    po::store(po::command_line_parser(argc, argv)
                  .options(desc)
                  .positional(pos_desc)
                  .run(),
              vm);
    po::notify(vm);

    if (vm.count("help")) {
      std::cout << desc << std::endl;
      return 0;
    }

    workingDir = getWorkingDirectory(
        vm.count("folder") ? vm["folder"].as<std::string>() : "");

    threads = vm["threads"].as<int>();
  } catch (const po::error &e) {
    std::cerr << "Could not handle arguments: " << e.what() << std::endl;
    return 1;
  }

  std::cout << "Working directory: " << workingDir << std::endl;

  boost::system::error_code ec;
  std::vector<fs::path> candidates;
  getWhitelistedFiles(workingDir, candidates);

  if (candidates.empty()) {
    std::cout << "Could not find any files to process";
    return 0;
  }

  boost::asio::thread_pool pool(threads);

  auto mp =
      MultilinePrinter("==================================== Processing... "
                       "====================================");

  auto start = std::chrono::high_resolution_clock::now();

  for (const auto &file : candidates) {
    boost::asio::post(pool,
                      [&file, &mp]() { processFile(file, mp.getStream("")); });
  }

  pool.join();
  auto end = std::chrono::high_resolution_clock::now();
  std::chrono::duration<double> duration = end - start;

  mp.setHeader("======================================== Done! "
               "========================================");
  std::cout << "Converting took " << duration.count() << " seconds"
            << std::endl;

  if (candidates.size()) {
    std::cout << "Remove old files? [N/y] ";
    char opt;
    std::cin >> opt;
    if (opt == 'y' || opt == 'Y')
      for (const auto &file : candidates)
        fs::remove(file, ec);
  }

  return 0;
}
