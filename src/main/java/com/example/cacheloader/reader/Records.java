package com.example.cacheloader.reader;

import com.fasterxml.jackson.databind.MappingIterator;
import java.io.Closeable;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.util.Map;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;

/** Bridges Jackson's iterator onto a stream that closes its source. */
final class Records {

  private Records() {}

  static Stream<Map<String, Object>> stream(
      MappingIterator<Map<String, Object>> rows, Closeable source) {
    Spliterator<Map<String, Object>> spliterator =
        Spliterators.spliteratorUnknownSize(rows, Spliterator.ORDERED | Spliterator.NONNULL);
    return StreamSupport.stream(spliterator, false)
        .onClose(
            () -> {
              try {
                rows.close();
                source.close();
              } catch (IOException e) {
                throw new UncheckedIOException("Failed to close record source", e);
              }
            });
  }
}
