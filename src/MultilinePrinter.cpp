#include "MultilinePrinter.hpp"

namespace {
void eraseLines(int count) {
  if (count > 0) {
    std::cout << "\x1b[2K";
    for (int i = 0; i < count; i++) {
      std::cout << "\x1b[1A"
                << "\x1b[2K";
    }
    std::cout << "\r";
  }
}
} // namespace

void LineStream::connectToOnClose(const std::function<void(std::string)> &f) {
  m_onClose.push_back(f);
}

void LineStream::connectToOnUpdate(const std::function<void(std::string)> &f) {
  m_onUpdate.push_back(f);
}

LineStream &LineStream::operator<<(const std::string &str) {
  auto lock = std::scoped_lock(m_mutex);
  m_text = str;
  for (const auto &callback : m_onUpdate)
    callback(str);

  return *this;
}

void LineStream::print(const std::string &str) { (*this) << str; }

LineStream::~LineStream() {
  for (const auto &callback : m_onClose)
    callback(m_text);
}

const std::string &LineStream::getText() const { return m_text; }

void MultilinePrinter::handleStreamClose(const std::string &str) {
  auto lock = std::scoped_lock(m_mutex);
  auto it = m_streams.begin();
  while (it != m_streams.end()) {
    if ((*it).expired())
      break;
    ++it;
  }

  if (it != m_streams.end()) {
    m_streams.erase(it);

    eraseLines(m_streams.size() + !m_header.empty() + 1);
    std::cout << str << std::endl;
    print();
  }
}

void MultilinePrinter::print() {
  if (m_header.size())
    std::cout << m_header << std::endl;

  for (const auto &stream : m_streams) {
    std::cout << ((stream.expired()) ? "" : stream.lock()->getText())
              << std::endl;
  }
}

void MultilinePrinter::update() {
  auto lock = std::scoped_lock(m_mutex);

  eraseLines(m_streams.size() + !m_header.empty());

  print();
}

void MultilinePrinter::setHeader(const std::string &str) {
  auto lock = std::scoped_lock(m_mutex);

  m_header = str;

  eraseLines(m_streams.size() + !m_header.empty());

  print();
}

LineStreamPtr MultilinePrinter::getStream(const std::string &startmsg) {
  LineStreamPtr res = std::make_shared<LineStream>(startmsg);
  res->connectToOnClose(std::bind(&MultilinePrinter::handleStreamClose, this,
                                  std::placeholders::_1));
  res->connectToOnUpdate(std::bind(&MultilinePrinter::update, this));

  auto lock = std::scoped_lock(m_mutex);
  m_streams.push_back(res);
  eraseLines(m_streams.size() + !m_header.empty() - 1);
  print();

  return res;
}
