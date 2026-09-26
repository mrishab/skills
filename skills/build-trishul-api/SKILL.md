---
name: build-trishul-api
description: Standardized workflow for creating new domain APIs within the Trishul framework, following the trishul-user module pattern. Use when building or extending Trishul domain interfaces, DTOs, mappers, services, controllers, or database migrations.
version: 1.0.0
---

# Trishul API Development

Guidelines for creating domain APIs within the Trishul framework, following the two-module architecture:
1. `trishul-<domain>`: API contract (Interfaces, Entities, DTOs, Mappers, Refreshers)
2. `trishul-<domain>-service`: Implementation (Repositories, Services, Controllers, Autoconfiguration, Migrations)

---

## 1. Domain Interface Hierarchy

### `Base<Entity>` Interface
Defines core domain attributes with `ATTR_*` string constants and fluent setters:

```java
package sh.trishul.user.model;

import java.net.URI;
import java.util.List;

public interface BaseUser<T extends BaseUser<T>> {
  String ATTR_DISPLAY_NAME = "displayName";
  String ATTR_EMAIL = "email";
  String ATTR_USER_NAME = "userName";

  String getDisplayName();
  T setDisplayName(String displayName);

  String getEmail();
  T setEmail(String email);

  String getUserName();
  T setUserName(String userName);
}
```

### `Update<Entity>` Interface
Extends `Base<Entity>` and `UpdatableEntity<Long, T>` for entities supporting updates:

```java
package sh.trishul.user.model;

import sh.trishul.base.types.base.pojo.UpdatableEntity;

public interface UpdateUser<T extends UpdateUser<T>> extends BaseUser<T>, UpdatableEntity<Long, T> {
}
```

### `<Entity>Accessor<T>` Interface
Accessor contract for composition in parent entities:

```java
package sh.trishul.user.model;

public interface UserAccessor<T extends UserAccessor<T>> {
  User getUser();
  T setUser(User user);
}
```

---

## 2. Model & DTO Implementations

### JPA Entity
Implements `CrudEntity<Long, Entity>`, `Update<Entity>`, and `Audited<Entity>`:

```java
package sh.trishul.user.model;

import jakarta.persistence.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import sh.trishul.base.types.base.pojo.Audited;
import sh.trishul.base.types.base.pojo.CrudEntity;
import sh.trishul.model.base.entity.BaseEntity;
import java.time.LocalDateTime;

@Entity(name = "user")
@Table(name = "_user")
@JsonIgnoreProperties({"hibernateLazyInitializer"})
public class User extends BaseEntity
    implements CrudEntity<Long, User>, UpdateUser<User>, Audited<User> {
  @Id
  @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "user_generator")
  @SequenceGenerator(name = "user_generator", sequenceName = "user_sequence", allocationSize = 1)
  private Long id;

  @Column(name = "user_name", nullable = false)
  private String userName;

  @Column(name = "email")
  private String email;

  @Version
  private Integer version;

  @CreationTimestamp
  @Column(name = "created_at", updatable = false)
  private LocalDateTime createdAt;

  @UpdateTimestamp
  @Column(name = "updated_at")
  private LocalDateTime updatedAt;

  // Constructors, getters, and fluent setters (return this;)
}
```

### Add DTO
Implements `Base<Entity>` with validation annotations:

```java
package sh.trishul.user.model;

import jakarta.validation.constraints.NotNull;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import sh.trishul.base.types.base.pojo.BaseModel;

@JsonIgnoreProperties(ignoreUnknown = true)
public class AddUserDto extends BaseModel implements BaseUser<AddUserDto> {
  @NotNull
  private String userName;
  private String email;

  @Override
  public String getUserName() { return userName; }
  @Override
  public AddUserDto setUserName(String userName) { this.userName = userName; return this; }

  @Override
  public String getEmail() { return email; }
  @Override
  public AddUserDto setEmail(String email) { this.email = email; return this; }
}
```

### Update DTO
Implements `Update<Entity>` with `@NotNull` on `id` and `version`:

```java
package sh.trishul.user.model;

import jakarta.validation.constraints.NotNull;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import sh.trishul.base.types.base.pojo.BaseModel;

@JsonIgnoreProperties(ignoreUnknown = true)
public class UpdateUserDto extends BaseModel implements UpdateUser<UpdateUserDto> {
  @NotNull private Long id;
  @NotNull private Integer version;
  private String userName;
  private String email;

  @Override public Long getId() { return id; }
  @Override public UpdateUserDto setId(Long id) { this.id = id; return this; }
  @Override public Integer getVersion() { return version; }
  @Override public UpdateUserDto setVersion(Integer version) { this.version = version; return this; }
  // ... getters and fluent setters for BaseUser fields
}
```

### Read DTO (`<Entity>Dto`)
Implements `Update<Entity>`, `Audited<EntityDto>`:

```java
package sh.trishul.user.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import sh.trishul.base.types.base.pojo.Audited;
import sh.trishul.base.types.base.pojo.BaseModel;
import java.time.LocalDateTime;

@JsonIgnoreProperties(ignoreUnknown = true)
public class UserDto extends BaseModel implements UpdateUser<UserDto>, Audited<UserDto> {
  private Long id;
  private String userName;
  private String email;
  private Integer version;
  private LocalDateTime createdAt;
  private LocalDateTime updatedAt;

  // Getters and fluent setters for all fields
}
```

---

## 3. Mapper & Refresher Integration

### Refresher Pattern
Resolves entity stubs from IDs during deserialization and cascade operations:

```java
package sh.trishul.user.model;

import java.util.Collection;
import java.util.List;
import sh.trishul.crud.service.Refresher;

public class UserRefresher implements Refresher<User, UserAccessor<?>> {
  private final UserService service;

  public UserRefresher(UserService service) { this.service = service; }

  @Override
  public void refresh(Collection<? extends UserAccessor<?>> accessors) {
    if (accessors == null || accessors.isEmpty()) return;
    List<Long> ids = accessors.stream()
      .map(UserAccessor::getUser)
      .filter(java.util.Objects::nonNull)
      .map(User::getId)
      .filter(java.util.Objects::nonNull)
      .toList();
    if (ids.isEmpty()) return;
    var entities = service.getEntities(ids);
    var entityMap = entities.stream().collect(java.util.stream.Collectors.toMap(User::getId, e -> e));
    accessors.forEach(a -> {
      if (a.getUser() != null && a.getUser().getId() != null) {
        a.setUser(entityMap.get(a.getUser().getId()));
      }
    });
  }
}
```

### MapStruct Mapper
Uses `nullValuePropertyMappingStrategy = IGNORE` and `@Context` for cycles:

```java
package sh.trishul.user.model;

import org.mapstruct.*;
import sh.trishul.model.mapper.CycleAvoidingMappingContext;
import java.util.List;

@Mapper(componentModel = "default", nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE)
public interface UserMapper {
  User fromAddDto(AddUserDto dto, @Context CycleAvoidingMappingContext ctx);
  User fromUpdateDto(UpdateUserDto dto, @Context CycleAvoidingMappingContext ctx);
  UserDto toDto(User entity, @Context CycleAvoidingMappingContext ctx);
  List<UserDto> toDtos(List<User> entities, @Context CycleAvoidingMappingContext ctx);
  void updateFromDto(UpdateUserDto dto, @MappingTarget User entity, @Context CycleAvoidingMappingContext ctx);
}
```

---

## 4. Implementation (Service Layer)

### Repository Interface
```java
package sh.trishul.user.service.user.service.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import sh.trishul.repo.jpa.repository.ExtendedRepository;
import sh.trishul.user.model.User;

public interface UserRepository
    extends JpaRepository<User, Long>, JpaSpecificationExecutor<User>, ExtendedRepository<Long> {
  @Override
  @Query("select count(u) > 0 from user u where u.id in (:ids)")
  boolean existsByIds(Iterable<Long> ids);

  @Override
  @Modifying
  @Query("delete from user u where u.id in (:ids)")
  int deleteByIds(Iterable<Long> ids);
}
```

### Service Implementation
Extends `BaseService` and implements `CrudService`:

```java
package sh.trishul.user.service.user.service.service;

import jakarta.transaction.Transactional;
import org.springframework.data.domain.Page;
import org.springframework.data.jpa.domain.Specification;
import sh.trishul.crud.service.BaseService;
import sh.trishul.crud.service.CrudService;
import sh.trishul.crud.service.EntityMergerService;
import sh.trishul.repo.jpa.repository.service.RepoService;
import sh.trishul.user.model.*;
import java.util.*;

@Transactional
public class UserService extends BaseService
    implements CrudService<Long, User, BaseUser<?>, UpdateUser<?>, UserAccessor<?>> {
  private final RepoService<Long, User, UserRepository> repoService;
  private final EntityMergerService<Long, User, BaseUser<?>, UpdateUser<?>> entityMergerService;

  public UserService(
      RepoService<Long, User, UserRepository> repoService,
      EntityMergerService<Long, User, BaseUser<?>, UpdateUser<?>> entityMergerService) {
    this.repoService = repoService;
    this.entityMergerService = entityMergerService;
  }

  @Override
  public User get(Long id) { return repoService.get(id); }

  @Override
  public List<User> getEntities(Collection<Long> ids) { return repoService.getEntities(ids); }

  @Override
  public List<User> add(Collection<? extends BaseUser<?>> dtos) {
    List<User> entities = dtos.stream().map(dto -> entityMergerService.getEntity(dto)).toList();
    return repoService.saveAll(entities);
  }

  @Override
  public List<User> update(Collection<? extends UpdateUser<?>> dtos) {
    List<User> entities = dtos.stream().map(dto -> entityMergerService.getEntity(dto)).toList();
    return repoService.saveAll(entities);
  }

  @Override
  public long delete(Collection<Long> ids) { return repoService.delete(ids); }

  @Override
  public boolean exists(Collection<Long> ids) { return repoService.exists(ids); }

  public Page<User> get(Specification<User> spec, Pageable pageable) {
    return repoService.getPage(spec, pageable);
  }
}
```

---

## 5. Controller Definition

```java
package sh.trishul.user.service.user.service.controller;

import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import sh.trishul.model.mapper.CycleAvoidingMappingContext;
import sh.trishul.user.model.*;
import sh.trishul.user.service.user.service.service.UserService;
import java.util.List;
import java.util.Set;

@RestController
@RequestMapping("/users")
@Tag(name = "User")
public class UserController {
  private final UserService service;
  private final UserMapper mapper;

  public UserController(UserService service, UserMapper mapper) {
    this.service = service;
    this.mapper = mapper;
  }

  @GetMapping
  public Page<UserDto> getAll(Pageable pageable) {
    return service.get(null, pageable).map(u -> mapper.toDto(u, new CycleAvoidingMappingContext()));
  }

  @GetMapping("/{id}")
  public UserDto getById(@PathVariable Long id) {
    return mapper.toDto(service.get(id), new CycleAvoidingMappingContext());
  }

  @PostMapping
  @ResponseStatus(HttpStatus.CREATED)
  public List<UserDto> add(@RequestBody @Valid List<AddUserDto> dtos) {
    return mapper.toDtos(service.add(dtos), new CycleAvoidingMappingContext());
  }

  @PutMapping
  public List<UserDto> update(@RequestBody @Valid List<UpdateUserDto> dtos) {
    return mapper.toDtos(service.update(dtos), new CycleAvoidingMappingContext());
  }

  @DeleteMapping
  public long delete(@RequestParam Set<Long> ids) {
    return service.delete(ids);
  }
}
```

---

## 6. Autoconfiguration

Register beans in `@Configuration`:

```java
package sh.trishul.user.service.user.service.configuration;

import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import sh.trishul.crud.service.EntityMergerService;
import sh.trishul.repo.jpa.repository.service.RepoService;
import sh.trishul.user.model.*;
import sh.trishul.user.service.user.service.repository.UserRepository;
import sh.trishul.user.service.user.service.service.UserService;

@Configuration
public class UserAutoconfiguration {
  @Bean
  @ConditionalOnMissingBean(UserMapper.class)
  public UserMapper userMapper() {
    return new UserMapperImpl();
  }

  @Bean
  @ConditionalOnMissingBean(UserService.class)
  public UserService userService(
      UserRepository repo,
      EntityMergerService<Long, User, BaseUser<?>, UpdateUser<?>> merger) {
    return new UserService(new RepoService<>(repo), merger);
  }

  @Bean
  @ConditionalOnMissingBean(UserRefresher.class)
  public UserRefresher userRefresher(UserService userService) {
    return new UserRefresher(userService);
  }
}
```

Register configuration class in `src/main/resources/META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`.

---

## 7. Database Migration

Path: `trishul-<domain>-service/src/main/resources/db/tenant_migrations/<domain>/V1__base.sql`

```sql
CREATE SEQUENCE user_sequence START WITH 1 INCREMENT BY 1;

CREATE TABLE _user (
  id BIGINT PRIMARY KEY,
  user_name VARCHAR(255) NOT NULL,
  email VARCHAR(255),
  version INT NOT NULL,
  created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
  updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
);
```

---

## 8. Build & Verification

```bash
# In backend/
make install
```
Confirm `backend/api/openapi.json` generated and tests pass.
