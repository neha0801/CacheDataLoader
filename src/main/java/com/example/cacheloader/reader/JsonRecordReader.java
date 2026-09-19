package com.example.cacheloader.reader;

import com.fasterxml.jackson.databind.MappingIterator;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.io.InputStream;
import java.util.Map;
import java.util.stream.Stream;
import org.springframework.core.io.Resource;

/**
 * Reads JSON objects. Accepts either a top-level array of objects or newline-delimited objects;
 * Jackson's {@code readValues} handles both.
 */
public class JsonRecordReader implements RecordReader {

  private final ObjectMapper mapper = new ObjectMapper();

  @Override
  public Stream<Map<String, Object>> read(Resource source) throws IOException {
    InputStream in = source.getInputStream();
    try {
      MappingIterator<Map<String, Object>> objects = mapper.readerFor(Map.class).readValues(in);
      return Records.stream(objects, in);
    } catch (IOException | RuntimeException e) {
      in.close();
      throw e;
    }
  }
}
