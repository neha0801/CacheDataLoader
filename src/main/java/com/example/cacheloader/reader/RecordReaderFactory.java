package com.example.cacheloader.reader;

import com.example.cacheloader.config.LoaderProperties.Format;
import org.springframework.stereotype.Component;

/** Picks a reader for the configured source format. */
@Component
public class RecordReaderFactory {

  public RecordReader forFormat(Format format) {
    return switch (format) {
      case CSV -> new CsvRecordReader();
      case JSON -> new JsonRecordReader();
    };
  }
}
