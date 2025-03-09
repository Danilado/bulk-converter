#pragma once

#include <boost/filesystem.hpp>
#include <boost/process.hpp>
#include <functional>
#include <string>
#include <unordered_map>

namespace bp = boost::process;
namespace fs = boost::filesystem;

class FFmpegRunner {
public:
  FFmpegRunner(const fs::path &inputFile,
               std::function<void(const std::string &)> callback)
      : m_callback(callback), m_input(inputFile){};
  ~FFmpegRunner() {
    if (m_subprocess.running())
      m_subprocess.terminate();
  }

  void run();

private:
  std::function<void(const std::string &)> m_callback;
  double m_duration = -1.;
  int m_prev_percent = -1;
  std::string out_file;
  fs::path m_input;
  bp::child m_subprocess;

  void analyzeProgressbar(const std::string &);

  std::unordered_map<std::string, std::string> m_ext_map = {
      {".mp4", ".webm"}, {".mov", ".webm"}, {".mkv", ".webm"},
      {".png", ".webp"}, {".jpg", ".webp"}, {".jpeg", ".webp"},
  };
};
