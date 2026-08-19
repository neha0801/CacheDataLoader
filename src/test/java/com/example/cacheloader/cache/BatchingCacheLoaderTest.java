package com.example.cacheloader.cache;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.IntStream;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;

class BatchingCacheLoaderTest {

  private static Map<String, Object> record(Object id, String name) {
    Map<String, Object> record = new LinkedHashMap<>();
    record.put("id", id);
    record.put("name", name);
    return record;
  }

  private static Stream<Map<String, Object>> records(int count) {
    return IntStream.rangeClosed(1, count).mapToObj(i -> record(i, "name-" + i));
  }

  @Test
  void flushesRemainderWhenCountIsNotAMultipleOfBatchSize() {
    RecordingCacheWriter writer = new RecordingCacheWriter();

    long loaded = new BatchingCacheLoader("id", 3).load(records(7), writer);

    assertThat(loaded).isEqualTo(7);
    assertThat(writer.batchSizes()).containsExactly(3, 3, 1);
    assertThat(writer.contents()).hasSize(7);
  }

  @Test
  void doesNotFlushAnEmptyTrailingBatch() {
    RecordingCacheWriter writer = new RecordingCacheWriter();

    long loaded = new BatchingCacheLoader("id", 3).load(records(6), writer);

    assertThat(loaded).isEqualTo(6);
    assertThat(writer.batchSizes()).containsExactly(3, 3);
  }

  @Test
  void writesNothingForAnEmptySource() {
    RecordingCacheWriter writer = new RecordingCacheWriter();

    long loaded = new BatchingCacheLoader("id", 10).load(Stream.of(), writer);

    assertThat(loaded).isZero();
    assertThat(writer.batchSizes()).isEmpty();
  }

  @Test
  void keysEntriesOnTheConfiguredField() {
    RecordingCacheWriter writer = new RecordingCacheWriter();

    new BatchingCacheLoader("name", 10)
        .load(Stream.of(record(1, "ada"), record(2, "grace")), writer);

    assertThat(writer.contents()).containsOnlyKeys("ada", "grace");
  }

  @Test
  void laterRecordsWinOnDuplicateKeys() {
    RecordingCacheWriter writer = new RecordingCacheWriter();

    long loaded =
        new BatchingCacheLoader("id", 10).load(Stream.of(record(1, "first"), record(1, "second")), writer);

    assertThat(loaded).isEqualTo(1);
    assertThat(writer.contents().get(1)).isEqualTo(record(1, "second"));
  }

  @Test
  void reportsTheRowNumberWhenTheKeyFieldIsMissing() {
    RecordingCacheWriter writer = new RecordingCacheWriter();
    List<Map<String, Object>> rows = List.of(record(1, "ada"), Map.of("name", "no-id-here"));

    assertThatThrownBy(() -> new BatchingCacheLoader("id", 10).load(rows.stream(), writer))
        .isInstanceOf(IllegalStateException.class)
        .hasMessageContaining("Record 2")
        .hasMessageContaining("'id'");
  }

  @Test
  void rejectsAnInvalidBatchSize() {
    assertThatThrownBy(() -> new BatchingCacheLoader("id", 0))
        .isInstanceOf(IllegalArgumentException.class)
        .hasMessageContaining("batchSize");
  }
}
