package com.example.cacheloader.reader;

import static org.assertj.core.api.Assertions.assertThat;

import com.example.cacheloader.config.LoaderProperties.Format;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.Resource;

class RecordReaderTest {

  private static Resource resource(String content) {
    return new ByteArrayResource(content.getBytes());
  }

  private static List<Map<String, Object>> readAll(RecordReader reader, Resource source)
      throws IOException {
    try (Stream<Map<String, Object>> records = reader.read(source)) {
      return records.toList();
    }
  }

  @Test
  void csvUsesTheHeaderRowAsFieldNames() throws IOException {
    List<Map<String, Object>> records =
        readAll(
            new CsvRecordReader(),
            resource("id,name,dept\n1,Ada,Engineering\n2,Grace,Research\n"));

    assertThat(records).hasSize(2);
    assertThat(records.get(0)).containsExactly(
        Map.entry("id", "1"), Map.entry("name", "Ada"), Map.entry("dept", "Engineering"));
    assertThat(records.get(1)).containsEntry("name", "Grace");
  }

  @Test
  void csvHandlesQuotedFieldsContainingCommas() throws IOException {
    List<Map<String, Object>> records =
        readAll(new CsvRecordReader(), resource("id,name\n1,\"Lovelace, Ada\"\n"));

    assertThat(records.get(0)).containsEntry("name", "Lovelace, Ada");
  }

  @Test
  void csvWithOnlyAHeaderYieldsNoRecords() throws IOException {
    assertThat(readAll(new CsvRecordReader(), resource("id,name\n"))).isEmpty();
  }

  @Test
  void jsonReadsATopLevelArray() throws IOException {
    List<Map<String, Object>> records =
        readAll(
            new JsonRecordReader(),
            resource("[{\"id\":1,\"name\":\"Ada\"},{\"id\":2,\"name\":\"Grace\"}]"));

    assertThat(records).hasSize(2);
    assertThat(records.get(0)).containsEntry("id", 1).containsEntry("name", "Ada");
  }

  @Test
  void jsonReadsNewlineDelimitedObjects() throws IOException {
    List<Map<String, Object>> records =
        readAll(
            new JsonRecordReader(),
            resource("{\"id\":1,\"name\":\"Ada\"}\n{\"id\":2,\"name\":\"Grace\"}\n"));

    assertThat(records).hasSize(2);
    assertThat(records.get(1)).containsEntry("id", 2);
  }

  @Test
  void jsonPreservesNumericAndBooleanTypes() throws IOException {
    List<Map<String, Object>> records =
        readAll(new JsonRecordReader(), resource("[{\"id\":7,\"active\":true}]"));

    assertThat(records.get(0).get("id")).isInstanceOf(Integer.class);
    assertThat(records.get(0).get("active")).isEqualTo(true);
  }

  @Test
  void factoryReturnsAReaderPerFormat() {
    RecordReaderFactory factory = new RecordReaderFactory();

    assertThat(factory.forFormat(Format.CSV)).isInstanceOf(CsvRecordReader.class);
    assertThat(factory.forFormat(Format.JSON)).isInstanceOf(JsonRecordReader.class);
  }

  @Test
  void readsTheBundledSampleDataset() throws IOException {
    List<Map<String, Object>> records =
        readAll(new CsvRecordReader(), new ClassPathResource("data/users.csv"));

    assertThat(records).hasSize(5);
    assertThat(records).allSatisfy(r -> assertThat(r).containsKeys("id", "name", "email", "department"));
  }
}
