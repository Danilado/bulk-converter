#include "Converter.hpp"

#include <chrono>
#include <format>
#include <iostream>
#include <regex>
#include <string>

namespace {

// Функция для перевода времени формата "00:00:07.360000" в секунды
double parseTimeToSeconds(const std::string &timeStr) {
  std::regex timeRegex(R"((\d+):(\d+):(\d+\.\d+))");
  std::smatch match;

  if (std::regex_search(timeStr, match, timeRegex)) {
    int hours = std::stoi(match[1].str());
    int minutes = std::stoi(match[2].str());
    double seconds = std::stod(match[3].str());

    return hours * 3600 + minutes * 60 + seconds;
  }
  return -1.0; // Ошибка парсинга
}

std::string generateProgressBar(int width, double progress) {
  int fillCount = static_cast<int>(width * progress);
  int emptyCount = width - fillCount;
  return "|" + std::string(fillCount, '#') + std::string(emptyCount, '.') + "|";
}

int percent(double progress) { return int(progress * 100); }

std::string formatName(const std::string &str, int length) {
  if (str.size() > length) {
    return str.substr(0, length - 3) + "...";
  } else {
    return str + std::string(length - str.size(), ' ');
  }
}

void copyDates(const fs::path &source, const fs::path &target) {
  std::string command =
      std::format("exiftool -q -TagsFromFile \"{}\" -FileModifyDate "
                  "-FileCreateDate -overwrite_original \"{}\"",
                  source.string(), target.string());

  try {
    bp::child exif(command);
    exif.wait();
  } catch (...) {
  }
}

} // namespace

void FFmpegRunner::run() {
  bp::ipstream pipe_stream;

  if (!fs::exists(m_input)) {
    m_callback(std::format("Could not find file {}", m_input.string()));
    return;
  }

  auto ext_it = m_ext_map.find(m_input.extension().string());
  if (ext_it == m_ext_map.end()) {
    m_callback(std::format("Could not find conversion format for file {}",
                           m_input.string()));
    return;
  }
  fs::path output = m_input;
  output.replace_extension(ext_it->second);

  // boost::system::error_code ec;
  // boost::filesystem::remove(output, ec);

  if (fs::exists(output)) {
    copyDates(m_input, output);
    m_callback(
        std::format("File {} already exists. Skipping...", output.string()));
    return;
  }

  m_callback(std::format("Starting conversion for {}", output.string()));
  std::string command = std::format(
      "ffmpeg -err_detect ignore_err -i \"{}\" \"{}\" -progress pipe:2",
      m_input.string(), output.string());

  out_file = formatName(output.filename().string(), 40);

  auto start = std::chrono::high_resolution_clock::now();
  // bp::child ffmpeg(command);
  bp::child ffmpeg(command, bp::std_err > pipe_stream);

  std::string line;

  while (pipe_stream && std::getline(pipe_stream, line)) {
    try {
      analyzeProgressbar(line);
    } catch (...) {
    }
  }

  ffmpeg.wait();
  auto end = std::chrono::high_resolution_clock::now();
  std::chrono::duration<double> duration = end - start;

  copyDates(m_input, output);

  m_callback(
      std::format("{} done in {} seconds", output.string(), duration.count()));
}

void FFmpegRunner::analyzeProgressbar(const std::string &str) {
  std::size_t pos;
  if ((pos = str.find("Duration: ")) != std::string::npos) {
    double time = ::parseTimeToSeconds(str.substr(pos + 10, 15));
    m_duration = time;
  } else if ((pos = str.find("out_time=")) != std::string::npos) {
    double time = ::parseTimeToSeconds(str.substr(pos + 9, 15));
    if (time < 0 || m_duration < 0)
      return;

    double progress = std::clamp(time / m_duration, 0., 1.);
    int perc = percent(progress);
    if (m_prev_percent != perc) {
      m_prev_percent = perc;
      m_callback(std::format("{} {} {}%", out_file,
                             generateProgressBar(40, progress), perc));
    }
  }
}
