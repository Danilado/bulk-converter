#pragma once

#include <boost/filesystem.hpp>
#include <boost/process.hpp>
#include <functional>
#include <string>
#include <unordered_map>

namespace fs = boost::filesystem;

class FFmpegRunner {
public:
  FFmpegRunner(const fs::path &inputFile,
               std::function<void(const std::string &)> callback)
      : m_callback(callback), m_input(inputFile){};
  void run();

private:
  std::function<void(const std::string &)> m_callback;
  double m_duration = 0;
  std::string out_file;
  fs::path m_input;

  void analyzeProgressbar(const std::string &);

  std::unordered_map<std::string, std::string> m_ext_map = {
      {".mp4", ".webm"}, {".mov", ".webm"}, {".mkv", ".webm"},
      {".png", ".webp"}, {".jpg", ".webp"}, {".jpeg", ".webp"},
  };
};
