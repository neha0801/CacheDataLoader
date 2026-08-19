package com.example.cacheloader.reader;

import com.fasterxml.jackson.databind.MappingIterator;
import com.fasterxml.jackson.dataformat.csv.CsvMapper;
import com.fasterxml.jackson.dataformat.csv.CsvSchema;
import java.io.IOException;
import java.io.InputStream;
import java.util.Map;
import java.util.stream.Stream;
import org.springframework.core.io.Resource;

/** Reads CSV where the first line holds the column names. */
public class CsvRecordReader implements RecordReader {

  private final CsvMapper mapper = new CsvMapper();

  @Override
  public Stream<Map<String, Object>> read(Resource source) throws IOException {
    CsvSchema schema = CsvSchema.emptySchema().withHeader();
    InputStream in = source.getInputStream();
    try {
      MappingIterator<Map<String, Object>> rows =
          mapper.readerFor(Map.class).with(schema).readValues(in);
      return Records.stream(rows, in);
    } catch (IOException | RuntimeException e) {
      in.close();
      throw e;
    }
  }
}
