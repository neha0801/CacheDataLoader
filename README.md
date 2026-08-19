# CacheDataLoader

A Spring Boot utility that bulk-loads data from a flat file into an Oracle
Coherence cache.

> **Status: scaffold.** The build and configuration are in place; the Java
> sources are not written yet. See [Current state](#current-state) below.

## What it is meant to do

Point it at a CSV or JSON file, name a target cache, and it loads the rows into
Coherence in batches on startup. The intended use is seeding a cache — at
application boot, after a cluster restart, or as a one-shot job — without
hand-writing a loader for each new data type.

## Configuration

All options live in [`application.yml`](application.yml):

| Key | Meaning | Default in repo |
| --- | --- | --- |
| `loader.cacheName` | Target Coherence cache | `users` |
| `loader.format` | Source format — `csv` or `json` | `csv` |
| `loader.source` | Input file; `classpath:` prefix reads from resources, otherwise an absolute path | `classpath:data/users.csv` |
| `loader.batchSize` | Rows per `putAll` call | `1000` |
| `coherence.cluster` | Coherence cluster name | `demo-cluster` |
| `coherence.cache-config` | Coherence cache config XML | `classpath:coherence-cache-config.xml` |

## Stack

- Java 17
- Spring Boot 3.3.2 (`spring-boot-starter`, `spring-boot-starter-validation`)
- Oracle Coherence CE 24.06 — swap to commercial Coherence by replacing the
  `com.oracle.coherence.ce` dependency in [`pom.xml`](pom.xml) with
  `com.oracle.coherence`; the coordinates are commented in place
- Jackson (`jackson-databind`, `jackson-dataformat-csv`) for parsing

## Build

```bash
mvn clean package
```

## Current state

What exists:

- `pom.xml` — dependencies, Java 17 toolchain, Spring Boot packaging
- `application.yml` — the loader and Coherence settings above

What is still needed to make it run:

- [ ] `src/main/java/…` — the Spring Boot application class
- [ ] A generic DAO / reader over the CSV and JSON formats
- [ ] The batching `putAll` writer against `NamedCache`
- [ ] `src/main/resources/coherence-cache-config.xml`
- [ ] `src/main/resources/data/users.csv` — the sample dataset the default
      config points at
- [ ] Tests (`spring-boot-starter-test` is already on the test classpath)

`mvn clean package` will produce an empty jar until the sources land.
