package com.example.cacheloader.reader;

import java.io.IOException;
import java.util.Map;
import java.util.stream.Stream;
import org.springframework.core.io.Resource;

/** Reads a source file into a stream of records, one map per row or object. */
public interface RecordReader {

  /**
   * Opens {@code source} and streams its records.
   *
   * <p>The returned stream holds the underlying input stream open; callers must close it, which
   * closes the source in turn.
   */
  Stream<Map<String, Object>> read(Resource source) throws IOException;
}
