# CacheDataLoader

A Spring Boot utility that bulk-loads a CSV or JSON file into an Oracle
Coherence cache.

Point it at a file, name a target cache, and it streams the rows in via
batched `putAll` calls. Useful for seeding a cache at boot, after a cluster
restart, or as a one-shot job — without hand-writing a loader per data type.

## Quick start

```bash
mvn clean package

java -Dcoherence.wka=127.0.0.1 -Dcoherence.localhost=127.0.0.1 -Dcoherence.ttl=0 \
     -jar target/coherence-cache-loader-spring-boot-0.0.1-SNAPSHOT.jar
```

Out of the box that loads the bundled sample (`src/main/resources/data/users.csv`)
into a cache named `users` and exits:

```
Loading classpath:data/users.csv into cache 'users' as CSV (batch size 1000)
Loaded 5 entries from 5 records
Loaded 5 entries into 'users' in 66 ms
```

The `coherence.*` system properties above pin the cluster to loopback, which is
what you want for a local single-member run. Drop them when joining a real
cluster.

## Configuration

Defaults live in [`src/main/resources/application.yml`](src/main/resources/application.yml);
any of them can be overridden on the command line.

| Key | Meaning | Default |
| --- | --- | --- |
| `loader.cacheName` | Target Coherence cache | `users` |
| `loader.format` | `csv` or `json` | `csv` |
| `loader.source` | Input file — `classpath:` prefix reads from resources, otherwise an absolute path | `classpath:data/users.csv` |
| `loader.keyField` | Field in each record used as the cache key | `id` |
| `loader.batchSize` | Rows per `putAll` call | `1000` |
| `loader.keepAlive` | Stay up after loading instead of exiting | `false` |
| `coherence.cluster` | Cluster name | `demo-cluster` |
| `coherence.cache-config` | Coherence cache config XML | `classpath:coherence-cache-config.xml` |

Loading a JSON file from disk into a different cache:

```bash
java -jar target/coherence-cache-loader-spring-boot-0.0.1-SNAPSHOT.jar \
     --loader.format=json \
     --loader.source=/data/people.json \
     --loader.cacheName=people \
     --loader.batchSize=500
```

## Input formats

**CSV** — the first line is the header and supplies the field names. Quoted
fields containing commas are handled. All values arrive as strings.

**JSON** — either a top-level array of objects, or newline-delimited objects.
Numbers and booleans keep their JSON types.

Each record becomes one cache entry: the value of `loader.keyField` is the key,
and the whole record (as a `Map`) is the value. A record missing that field
fails the load and names the offending row number. Records sharing a key
overwrite one another, matching cache semantics.

## Design

```
CacheLoadRunner          resolves the source, wires the pieces, runs once at startup
  └── RecordReaderFactory
        ├── CsvRecordReader     ─┐
        └── JsonRecordReader    ─┴─ stream Map<String,Object> records
  └── BatchingCacheLoader   keys each record, flushes fixed-size batches
        └── CacheWriter
              └── CoherenceCacheWriter   putAll against a NamedCache
```

Records are streamed rather than read into memory, so file size is not bounded
by heap. `CacheWriter` is an interface so the batching logic can be tested
without standing up a cluster.

## Stack

- Java 17
- Spring Boot 3.3.2
- Oracle Coherence CE 24.09.3 — to use commercial Coherence, swap the
  `com.oracle.coherence.ce` dependency in [`pom.xml`](pom.xml) for
  `com.oracle.coherence`; the coordinates are commented in place
- Jackson (`jackson-databind`, `jackson-dataformat-csv`)

## Tests

```bash
mvn test
```

15 tests covering batch boundaries, key extraction, duplicate keys, missing-key
errors, and both readers. They do not require a running cluster.
