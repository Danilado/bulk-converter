#pragma once

#include <atomic>
#include <functional>
#include <iostream>
#include <memory>
#include <mutex>
#include <string>
#include <unordered_map>
#include <vector>

class LineStream {
private:
  std::vector<std::function<void(std::string)>> m_onUpdate;
  std::vector<std::function<void(std::string)>> m_onClose;

  std::string m_text;

public:
  LineStream(const std::string &defaultText = "") : m_text(defaultText){};
  ~LineStream();

  void connectToOnClose(const std::function<void(std::string)> &f);
  void connectToOnUpdate(const std::function<void(std::string)> &f);

  LineStream &operator<<(const std::string &str);
  void print(const std::string &str);
  const std::string &getText() const;
};

using LineStreamPtr = std::shared_ptr<LineStream>;
using LineStreamWPtr = std::weak_ptr<LineStream>;

class MultilinePrinter {
private:
  std::mutex m_mutex;
  std::vector<LineStreamWPtr> m_streams;
  std::string m_header = "";
  std::atomic<int> m_offset = 0;

  void handleStreamClose(const std::string &);
  void update();
  void print();

public:
  MultilinePrinter(const std::string &header) : m_header(header) {
    if (header.size())
      std::cout << header << std::endl;
  };
  ~MultilinePrinter() = default;

  void setHeader(const std::string &str);
  LineStreamPtr getStream(const std::string &startmsg);
};
