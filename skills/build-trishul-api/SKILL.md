---
name: build-trishul-api
description: Standardized workflow for creating new domain APIs within the Trishul framework, following the trishul-user module pattern. Use when building or extending Trishul domain interfaces, DTOs, mappers, services, controllers, or database migrations.
version: 1.0.0
---

# Trishul API Development Skill

This skill provides a standardized workflow for creating new domain APIs within the Trishul framework, following the pattern established by the `trishul-user` module.

## Architecture Overview

A domain API in Trishul is typically split into two modules:
1.  **`trishul-<domain>`**: Contains the API contract (Interfaces, Entities, DTOs, Mappers, Refreshers).
2.  **`trishul-<domain>-service`**: Contains the implementation (Repositories, Services, Controllers, Autoconfiguration, Database Migrations).

## Domain Interface Hierarchy

Trishul uses a strict interface hierarchy to maintain consistency across Entities and DTOs.

### 1. `Base<Entity>` Interface
- **Purpose**: Defines core domain attributes shared by all representations. This interface establishes the common contract for an entity across different layers (DTOs, persistence) and ensures type safety with recursive generics.
- **Attributes**: Define all property names as `public static final String` constants (e.g., `String ATTR_NAME = "name"`). These constants are crucial for type-safe mapping and attribute filtering.
- **Methods**: Define getters and fluent setters (returning `T` for method chaining).
- **Example**:
  ```java
package sh.trishul.user.model;

import java.net.URI;
import java.util.List;
import sh.trishul.user.role.model.UserRole;
import sh.trishul.user.salutation.model.UserSalutationAccessor;
import sh.trishul.user.status.UserStatusAccessor;

public interface BaseUser<T extends BaseUser<T>>
    extends UserStatusAccessor<T>, UserSalutationAccessor<T> {
  final String ATTR_DISPLAY_NAME = "displayName";
  final String ATTR_FIRST_NAME = "firstName";
  final String ATTR_LAST_NAME = "lastName";
  final String ATTR_EMAIL = "email";
  final String ATTR_IMAGE_SRC = "imageSrc";
  final String ATTR_PHONE_NUMBER = "phoneNumber";
  final String ATTR_USER_NAME = "userName";
  final String ATTR_IAAS_USERNAME = "iaasUsername";
  final String ATTR_ROLES = "roles";

  String getDisplayName();

  T setDisplayName(String displayName);

  String getFirstName();

  T setFirstName(String firstName);

  String getLastName();

  T setLastName(String lastName);

  String getEmail();

  T setEmail(String email);

  URI getImageSrc();

  T setImageSrc(URI imageSrc);

  String getPhoneNumber();

  T setPhoneNumber(String phoneNumber);

  String getUserName();

  T setUserName(String userName);

  String getIaasUsername();

  T setIaasUsername(String iaasUsername);

  List<UserRole> getRoles();

  T setRoles(List<UserRole> roles);
}
  ```

### 2. `Update<Entity>` Interface
- **Purpose**: Extends the base interface for entities that can be updated. It includes fields necessary for identifying and managing concurrent updates (like `id` and `version`).
- **Hierarchy**: Extends `Base<Entity>` and `UpdatableEntity<Long, T>`.
- **Key Difference**: Inherits `getId()` from `Identified` and `getVersion()` from `Versioned` (via `UpdatableEntity`), making it suitable for representing updatable entities.
- **Example**:
  ```java
package sh.trishul.user.model;

import sh.trishul.base.types.base.pojo.UpdatableEntity;

public interface UpdateUser<T extends UpdateUser<T>> extends BaseUser<T>, UpdatableEntity<Long, T> {
}
  ```

### 3. Implementation Patterns

This section details the concrete implementations of Entities, DTOs, and Accessors, adhering to the defined interfaces and framework conventions.

#### Entity Definition

The JPA entity represents the persistent state of a domain object. It defines the table mapping, primary keys, relationships, and auditing fields.

##### Entity Example

```java
package sh.trishul.user.model;

import java.net.URI;
import java.net.URISyntaxException;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonManagedReference;

import sh.trishul.base.types.base.pojo.Audited;
import sh.trishul.base.types.base.pojo.CrudEntity;
import sh.trishul.model.base.entity.BaseEntity;
import sh.trishul.model.base.entity.CriteriaJoin;
import sh.trishul.user.role.binding.model.UserRoleBinding;
import sh.trishul.user.role.model.UserRole;
import sh.trishul.user.role.model.UserRoleAccessor;
import sh.trishul.user.salutation.model.UserSalutation;
import sh.trishul.user.status.UserStatus;
import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.OneToMany;
import jakarta.persistence.SequenceGenerator;
import jakarta.persistence.Table;
import jakarta.persistence.Version;
import jakarta.validation.constraints.Email;

@Entity(name = "user")
@Table(name = "_user")
@JsonIgnoreProperties({"hibernateLazyInitializer"})
public class User extends BaseEntity
    implements CrudEntity<Long, User>, UpdateUser<User>, Audited<User> {
  @Id @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "user_generator")
  @SequenceGenerator(name = "user_generator", sequenceName = "user_sequence", allocationSize = 1)
  private Long id;

  @Column(name = "user_name")
  private String userName;

  @Column(name = "iaas_username", updatable = false)
  private String iaasUsername;

  @Column(name = "display_name")
  private String displayName;

  @Column(name = "first_name")
  private String firstName;

  @Column(name = "last_name")
  private String lastName;

  @Column(name = "email", updatable = false, unique = true)
  @Email
  private String email;

  @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, orphanRemoval = true,
      fetch = FetchType.LAZY)
  @JsonManagedReference @CriteriaJoin
  private List<UserRoleBinding> roleBindings;

  @Column(name = "image_source")
  private String imageSrc;

  @Column(name = "phone_number")
  private String phoneNumber;

  @ManyToOne(fetch = FetchType.LAZY)
  @JoinColumn(name = "user_status_id", referencedColumnName = "id")
  private UserStatus status;

  @ManyToOne(fetch = FetchType.LAZY)
  @JoinColumn(name = "user_salutation_id", referencedColumnName = "id")
  private UserSalutation salutation;

  @Version
  private Integer version;

  @CreationTimestamp @Column(name = "created_at", updatable = false)
  private LocalDateTime createdAt;

  @UpdateTimestamp @Column(name = "last_updated")
  private LocalDateTime lastUpdated;

  public User() {}

  public User(Long id) {
    this();
    setId(id);
  }

  public User(Long id, String userName, String displayName, String firstName, String lastName,
      String email, String phoneNumber, URI imageSrc, String iaasUsername, UserStatus status,
      UserSalutation salutation, List<UserRole> roles, LocalDateTime createdAt,
      LocalDateTime lastUpdated, Integer version) {
    this(id);
    setUserName(userName);
    setDisplayName(displayName);
    setFirstName(firstName);
    setLastName(lastName);
    setEmail(email);
    setPhoneNumber(phoneNumber);
    setStatus(status);
    setImageSrc(imageSrc);
    setRoles(roles);
    setSalutation(salutation);
    setCreatedAt(createdAt);
    setLastUpdated(lastUpdated);
    setVersion(version);
  }

  @Override
  public Long getId() {
    return id;
  }

  @Override
  public User setId(Long id) {
    this.id = id;
    return this;
  }

  @Override
  public String getDisplayName() {
    return displayName;
  }

  @Override
  public User setDisplayName(String displayName) {
    this.displayName = displayName;
    return this;
  }

  @Override
  public String getFirstName() {
    return firstName;
  }

  @Override
  public User setFirstName(String firstName) {
    this.firstName = firstName;
    return this;
  }

  @Override
  public String getLastName() {
    return lastName;
  }

  @Override
  public User setLastName(String lastName) {
    this.lastName = lastName;
    return this;
  }

  @Override
  public String getEmail() {
    return email;
  }

  @Override
  public User setEmail(String email) {
    this.email = email;
    return this;
  }

  @Override
  public URI getImageSrc() {
    URI uri = null;
    if (this.imageSrc != null) {
      try {
        uri = new URI(this.imageSrc);
      } catch (URISyntaxException e) {
        throw new RuntimeException(
            String.format("Failed to convert to URI, value: %s", this.imageSrc), e);
      }
    }

    return uri;
  }

  @Override
  public User setImageSrc(URI imageSrc) {
    if (imageSrc != null) {
      this.imageSrc = imageSrc.toString();
    } else {
      this.imageSrc = null;
    }
    return this;
  }

  @Override
  public String getPhoneNumber() {
    return phoneNumber;
  }

  @Override
  public User setPhoneNumber(String phoneNumber) {
    this.phoneNumber = phoneNumber;
    return this;
  }

  @Override
  public UserStatus getStatus() {
    return status == null ? null : status.deepClone();
  }

  @Override
  public User setStatus(UserStatus status) {
    this.status = status == null ? null : status.deepClone();
    return this;
  }

  @Override
  public Integer getVersion() {
    return version;
  }

  public User setVersion(Integer version) {
    this.version = version;
    return this;
  }

  @Override
  public String getUserName() {
    return userName;
  }

  @Override
  public User setUserName(String userName) {
    this.userName = userName;
    return this;
  }

  @Override
  public String getIaasUsername() {
    return iaasUsername;
  }

  @Override
  public User setIaasUsername(String iaasUsername) {
    this.iaasUsername = iaasUsername;
    return this;
  }

  @Override
  public User setRoles(List<UserRole> roles) {
    if (roles == null) {
      if (this.roleBindings != null) {
        this.roleBindings.clear();
      } else {
        this.roleBindings = null;
      }
      return this;
    }

    // Reusing existing bindings instead of adding new to avoid creating dangling
    // child
    // entities.
    if (roleBindings == null) {
      roleBindings = new ArrayList<>();
    }

    Map<Long, UserRoleBinding> existingBindings = roleBindings.stream()
        .collect(Collectors.toMap(binding -> binding.getRole().getId(), binding -> binding));
    this.roleBindings.clear();
    roles.forEach(role -> {
      UserRoleBinding existing = existingBindings.remove(role.getId());
      if (existing == null) {
        existing = new UserRoleBinding();
      }

      existing.setRole(role);
      existing.setUser(this);

      this.roleBindings.add(existing);
    });
    return this;
  }

  @Override
  public List<UserRole> getRoles() {
    if (this.roleBindings == null) {
      return Collections.emptyList();
    }

    return this.roleBindings.stream().map(UserRoleAccessor::getRole).toList();
  }

  /**
   * Used by the repository to directly access the bindings. Refrain from using this is business
   * logic. Prefer, getRoles() method.
   *
   * @return
   */
  public List<UserRoleBinding> getRoleBindings() {
    return new ArrayList<>(this.roleBindings);
  }

  @Override
  public UserSalutation getSalutation() {
    return salutation == null ? null : salutation.deepClone();
  }

  @Override
  public User setSalutation(UserSalutation salutation) {
    this.salutation = salutation == null ? null : salutation.deepClone();
    return this;
  }

  @Override
  public LocalDateTime getLastUpdated() {
    return lastUpdated;
  }

  @Override
  public User setLastUpdated(LocalDateTime lastUpdated) {
    this.lastUpdated = lastUpdated;
    return this;
  }

  @Override
  public LocalDateTime getCreatedAt() {
    return createdAt;
  }

  @Override
  public User setCreatedAt(LocalDateTime createdAt) {
    this.createdAt = createdAt;
    return this;
  }
}
```

#### Accessor Interface

Accessor interfaces define methods to retrieve and set a specific domain entity within another object. This pattern is used for dependency injection and object graph traversal within the framework.

##### Accessor Example

```java
package sh.trishul.user.model;

public interface UserAccessor<T extends UserAccessor<T>> {
  final String ATTR_USER = "user";

  User getUser();

  T setUser(User user);
}
```

#### Add DTO

The Add DTO is used for creating new entities. It contains all necessary fields for creation, along with validation annotations.

##### Add DTO Example

```java
package sh.trishul.user.model;

import java.net.URI;
import java.util.ArrayList;
import java.util.List;
import sh.trishul.model.base.dto.BaseDto;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;

public class AddUserDto extends BaseDto {
  @NotBlank
  private String userName;

  @NotBlank
  private String displayName;

  @NotBlank
  private String firstName;

  @NotBlank
  private String lastName;

  @NotBlank @Email
  private String email;

  @NotNull
  private Long statusId;

  private Long salutationId;

  private String phoneNumber;

  @NotEmpty
  private List<Long> roleIds;

  private URI imageSrc;

  public AddUserDto() {}

  public AddUserDto( @NotBlank String userName, @NotBlank String displayName,
      @NotBlank String firstName, @NotBlank String lastName, @NotBlank String email,
      @NotNull Long statusId, @NotNull Long salutationId, @NotBlank String phoneNumber,
      URI imageSrc, List<Long> roleIds) {
    setUserName(userName);
    setDisplayName(displayName);
    setFirstName(firstName);
    setLastName(lastName);
    setEmail(email);
    setStatusId(statusId);
    setSalutationId(salutationId);
    setPhoneNumber(phoneNumber);
    setImageSrc(imageSrc);
    setRoleIds(roleIds);
  }

  public String getUserName() {
    return userName;
  }

  public AddUserDto setUserName(String userName) {
    this.userName = userName;
    return this;
  }

  public String getDisplayName() {
    return displayName;
  }

  public AddUserDto setDisplayName(String displayName) {
    this.displayName = displayName;
    return this;
  }

  public String getFirstName() {
    return firstName;
  }

  public AddUserDto setFirstName(String firstName) {
    this.firstName = firstName;
    return this;
  }

  public String getLastName() {
    return lastName;
  }

  public AddUserDto setLastName(String lastName) {
    this.lastName = lastName;
    return this;
  }

  public String getEmail() {
    return email;
  }

  public AddUserDto setEmail(String email) {
    this.email = email;
    return this;
  }

  public Long getStatusId() {
    return statusId;
  }

  public AddUserDto setStatusId(Long statusId) {
    this.statusId = statusId;
    return this;
  }

  public Long getSalutationId() {
    return salutationId;
  }

  public AddUserDto setSalutationId(Long salutationId) {
    this.salutationId = salutationId;
    return this;
  }

  public String getPhoneNumber() {
    return phoneNumber;
  }

  public AddUserDto setPhoneNumber(String phoneNumber) {
    this.phoneNumber = phoneNumber;
    return this;
  }

  public List<Long> getRoleIds() {
    return roleIds == null ? null : new ArrayList<>(roleIds);
  }

  public AddUserDto setRoleIds(List<Long> roleIds) {
    this.roleIds = roleIds == null ? null : new ArrayList<>(roleIds);
    return this;
  }

  public URI getImageSrc() {
    return imageSrc;
  }

  public AddUserDto setImageSrc(URI imageSrc) {
    this.imageSrc = imageSrc;
    return this;
  }
}
```

#### Update DTO

The Update DTO is used for updating existing entities. It includes the entity's `id` and `version` for optimistic locking, and uses `@NullOrNotBlank` for optional fields.

##### Update DTO Example

```java
package sh.trishul.user.model;

import java.net.URI;
import java.util.ArrayList;
import java.util.List;
import sh.trishul.model.base.dto.BaseDto;
import sh.trishul.model.validation.NullOrNotBlank;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public class UpdateUserDto extends BaseDto {
  private Long id;

  @NullOrNotBlank
  private String userName;

  @NullOrNotBlank
  private String displayName;

  @NullOrNotBlank
  private String firstName;

  @NullOrNotBlank
  private String lastName;

  @NullOrNotBlank @Email
  private String email;

  private Long statusId;

  private Long salutationId;

  @NullOrNotBlank
  private String phoneNumber;

  private URI imageSrc;

  @Size(min = 1)
  private List<Long> roleIds;

  @NotNull
  private Integer version;

  public UpdateUserDto() {
    super();
  }

  public UpdateUserDto(Long id) {
    this();
    setId(id);
  }

  public UpdateUserDto(Long id, String userName, String displayName, String firstName,
      String lastName, String email, Long statusId, Long salutationId, String phoneNumber,
      URI imageSrc, List<Long> roleIds, @NotNull Integer version) {
    this(id);
    setUserName(userName);
    setDisplayName(displayName);
    setFirstName(firstName);
    setLastName(lastName);
    setEmail(email);
    setStatusId(statusId);
    setSalutationId(salutationId);
    setPhoneNumber(phoneNumber);
    setRoleIds(roleIds);
    setImageSrc(imageSrc);
    setVersion(version);
  }

  public Long getId() {
    return id;
  }

  public UpdateUserDto setId(Long id) {
    this.id = id;
    return this;
  }

  public String getUserName() {
    return userName;
  }

  public UpdateUserDto setUserName(String userName) {
    this.userName = userName;
    return this;
  }

  public String getDisplayName() {
    return displayName;
  }

  public UpdateUserDto setDisplayName(String displayName) {
    this.displayName = displayName;
    return this;
  }

  public String getFirstName() {
    return firstName;
  }

  public UpdateUserDto setFirstName(String firstName) {
    this.firstName = firstName;
    return this;
  }

  public String getLastName() {
    return lastName;
  }

  public UpdateUserDto setLastName(String lastName) {
    this.lastName = lastName;
    return this;
  }

  public String getEmail() {
    return email;
  }

  public UpdateUserDto setEmail(String email) {
    this.email = email;
    return this;
  }

  public Long getStatusId() {
    return statusId;
  }

  public UpdateUserDto setStatusId(Long statusId) {
    this.statusId = statusId;
    return this;
  }

  public Long getSalutationId() {
    return salutationId;
  }

  public UpdateUserDto setSalutationId(Long salutationId) {
    this.salutationId = salutationId;
    return this;
  }

  public String getPhoneNumber() {
    return phoneNumber;
  }

  public UpdateUserDto setPhoneNumber(String phoneNumber) {
    this.phoneNumber = phoneNumber;
    return this;
  }

  public List<Long> getRoleIds() {
    return roleIds == null ? null : new ArrayList<>(roleIds);
  }

  public UpdateUserDto setRoleIds(List<Long> roleIds) {
    this.roleIds = roleIds == null ? null : new ArrayList<>(roleIds);
    return this;
  }

  public URI getImageSrc() {
    return imageSrc;
  }

  public UpdateUserDto setImageSrc(URI imageSrc) {
    this.imageSrc = imageSrc;
    return this;
  }

  public Integer getVersion() {
    return version;
  }

  public UpdateUserDto setVersion(Integer version) {
    this.version = version;
    return this;
  }
}
```

#### Read DTO

The Read DTO is used for presenting data to clients. It includes all fields necessary for display and uses DTOs for nested relationships.

##### Read DTO Example

```java
package sh.trishul.user.model;

import sh.trishul.model.base.dto.BaseDto;
import sh.trishul.object.store.file.model.accessor.DecoratedIaasObjectStoreFileAccessor;
import sh.trishul.object.store.file.model.dto.IaasObjectStoreFileDto;
import sh.trishul.user.role.model.UserRoleDto;
import sh.trishul.user.salutation.model.UserSalutationDto;
import sh.trishul.user.status.UserStatusDto;
import java.net.URI;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

public class UserDto extends BaseDto implements DecoratedIaasObjectStoreFileAccessor<UserDto> {
  private Long id;

  private String userName;

  private String iaasUsername;

  private String displayName;

  private String firstName;

  private String lastName;

  private String email;

  private String phoneNumber;

  private URI imageSrc;

  private IaasObjectStoreFileDto objectStoreFile;

  private UserStatusDto status;

  private UserSalutationDto salutation;

  private List<UserRoleDto> roles;

  private LocalDateTime createdAt;

  private LocalDateTime lastUpdated;

  private Integer version;

  public UserDto() {}

  public UserDto(Long id) {
    this();
    setId(id);
  }

  public UserDto(Long id, String userName, String displayName, String firstName, String lastName,
      String email, String phoneNumber, URI imageSrc, IaasObjectStoreFileDto objectStoreFile,
      UserStatusDto status, UserSalutationDto salutation, List<UserRoleDto> roles,
      LocalDateTime createdAt, LocalDateTime lastUpdated, Integer version) {
    this(id);
    setUserName(userName);
    setDisplayName(displayName);
    setFirstName(firstName);
    setLastName(lastName);
    setEmail(email);
    setPhoneNumber(phoneNumber);
    setImageSrc(imageSrc);
    setObjectStoreFile(objectStoreFile);
    setStatus(status);
    setSalutation(salutation);
    setRoles(roles);
    setCreatedAt(createdAt);
    setLastUpdated(lastUpdated);
    setLastName(lastName);
    setVersion(version);
  }

  public Long getId() {
    return id;
  }

  public UserDto setId(Long id) {
    this.id = id;
    return this;
  }

  public String getUserName() {
    return userName;
  }

  public UserDto setUserName(String userName) {
    this.userName = userName;
    return this;
  }

  public String getIaasUsername() {
    return iaasUsername;
  }

  public UserDto setIaasUsername(String iaasUsername) {
    this.iaasUsername = iaasUsername;
    return this;
  }

  public String getDisplayName() {
    return displayName;
  }

  public UserDto setDisplayName(String displayName) {
    this.displayName = displayName;
    return this;
  }

  public String getFirstName() {
    return firstName;
  }

  public UserDto setFirstName(String firstName) {
    this.firstName = firstName;
    return this;
  }

  public String getLastName() {
    return lastName;
  }

  public UserDto setLastName(String lastName) {
    this.lastName = lastName;
    return this;
  }

  public String getEmail() {
    return email;
  }

  public UserDto setEmail(String email) {
    this.email = email;
    return this;
  }

  public UserStatusDto getStatus() {
    return status;
  }

  public UserDto setStatus(UserStatusDto status) {
    this.status = status;
    return this;
  }

  public UserSalutationDto getSalutation() {
    return salutation;
  }

  public UserDto setSalutation(UserSalutationDto salutation) {
    this.salutation = salutation;
    return this;
  }

  public String getPhoneNumber() {
    return phoneNumber;
  }

  public UserDto setPhoneNumber(String phoneNumber) {
    this.phoneNumber = phoneNumber;
    return this;
  }

  public List<UserRoleDto> getRoles() {
    return roles == null ? null : new ArrayList<>(roles);
  }

  public UserDto setRoles(List<UserRoleDto> roles) {
    this.roles = roles == null ? null : new ArrayList<>(roles);
    return this;
  }

  @Override
  public URI getImageSrc() {
    return this.imageSrc;
  }

  public UserDto setImageSrc(URI imageSrc) {
    this.imageSrc = imageSrc;
    return this;
  }

  public IaasObjectStoreFileDto getObjectStoreFile() {
    return this.objectStoreFile;
  }

  @Override
  public UserDto setObjectStoreFile(IaasObjectStoreFileDto objectStoreFile) {
    this.objectStoreFile = objectStoreFile;
    return this;
  }

  public LocalDateTime getCreatedAt() {
    return createdAt;
  }

  public UserDto setCreatedAt(LocalDateTime createdAt) {
    this.createdAt = createdAt;
    return this;
  }

  public LocalDateTime getLastUpdated() {
    return lastUpdated;
  }

  public UserDto setLastUpdated(LocalDateTime lastUpdated) {
    this.lastUpdated = lastUpdated;
    return this;
  }

  public Integer getVersion() {
    return version;
  }

  public UserDto setVersion(Integer version) {
    this.version = version;
    return this;
  }
}
```

#### Refresher Implementation

Refresher implementations are responsible for enriching entities or DTOs by resolving their associated accessor IDs into full objects.

##### Refresher Example

```java
package sh.trishul.user.model;

import sh.trishul.base.types.base.pojo.OwnedByAccessor;
import sh.trishul.base.types.base.pojo.Refresher;
import sh.trishul.model.base.pojo.refresher.accessor.AccessorRefresher;
import sh.trishul.user.role.binding.model.UserRoleBinding;
import sh.trishul.user.role.binding.model.UserRoleBindingAccessor;
import sh.trishul.user.salutation.model.UserSalutation;
import sh.trishul.user.salutation.model.UserSalutationAccessor;
import sh.trishul.user.status.UserStatus;
import sh.trishul.user.status.UserStatusAccessor;
import java.util.Collection;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;

public class UserRefresher implements Refresher<User, UserAccessor<?>> {
  @SuppressWarnings("unused")
  private static final Logger log = LoggerFactory.getLogger(UserRefresher.class);

  private final AccessorRefresher<Long, UserAccessor<?>, User> refresher;
  private final AccessorRefresher<Long, AssignedToAccessor<?>, User> assignedToAccessorRefresher;
  private final AccessorRefresher<Long, OwnedByAccessor<User>, User> ownedByAccessorRefresher;
  private final Refresher<UserStatus, UserStatusAccessor<?>> statusRefresher;
  private final Refresher<UserSalutation, UserSalutationAccessor<?>> salutationRefresher;
  private final Refresher<UserRoleBinding, UserRoleBindingAccessor<?>> roleBindingRefresher;

  @Autowired
  public UserRefresher(AccessorRefresher<Long, UserAccessor<?>, User> refresher,
      AccessorRefresher<Long, AssignedToAccessor<?>, User> assignedToAccessorRefresher,
      AccessorRefresher<Long, OwnedByAccessor<User>, User> ownedByAccessorRefresher,
      Refresher<UserStatus, UserStatusAccessor<?>> statusRefresher,
      Refresher<UserSalutation, UserSalutationAccessor<?>> salutationRefresher,
      Refresher<UserRoleBinding, UserRoleBindingAccessor<?>> roleBindingRefresher) {
    this.refresher = refresher;
    this.assignedToAccessorRefresher = assignedToAccessorRefresher;
    this.ownedByAccessorRefresher = ownedByAccessorRefresher;
    this.statusRefresher = statusRefresher;
    this.salutationRefresher = salutationRefresher;
    this.roleBindingRefresher = roleBindingRefresher;
  }

  @Override
  public void refresh(Collection<User> users) {
    this.statusRefresher.refreshAccessors(users);
    this.salutationRefresher.refreshAccessors(users);

    List<UserRoleBinding> bindings = users.stream()
        .filter(u -> u != null && u.getRoleBindings() != null && !u.getRoleBindings().isEmpty())
        .flatMap(u -> u.getRoleBindings().stream()).toList();
    this.roleBindingRefresher.refresh(bindings);
  }

  @Override
  public void refreshAccessors(Collection<? extends UserAccessor<?>> accessors) {
    refresher.refreshAccessors(accessors);
  }

  public void refreshAssignedToAccessors(Collection<? extends AssignedToAccessor<?>> accessors) {
    assignedToAccessorRefresher.refreshAccessors(accessors);
  }

  public void refreshOwnedByAccessors(Collection<? extends OwnedByAccessor<User>> accessors) {
    ownedByAccessorRefresher.refreshAccessors(accessors);
  }
}
```

## Mapper Integration

MapStruct is used for mapping between Entities and DTOs. Mappers should extend `BaseMapper` and leverage the `ATTR_*` constants from the domain interfaces for type safety.

### Mapper Example

Below is a complete example of a `UserMapper`, demonstrating common patterns like ignoring fields, mapping by source, and using other mappers for nested objects.

```java
package sh.trishul.user.model;

import sh.trishul.model.base.mapper.BaseMapper;
import sh.trishul.user.role.model.UserRoleMapper;
import sh.trishul.user.salutation.model.UserSalutationMapper;
import sh.trishul.user.status.UserStatusMapper;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.factory.Mappers;

@Mapper(uses = {UserStatusMapper.class, UserSalutationMapper.class, UserRoleMapper.class})
public interface UserMapper extends BaseMapper<User, UserDto, AddUserDto, UpdateUserDto> {
  UserMapper INSTANCE = Mappers.getMapper(UserMapper.class);

  @Mapping(target = User.ATTR_ROLE_BINDINGS, ignore = true)
  @Mapping(target = User.ATTR_LAST_UPDATED, ignore = true)
  @Mapping(target = User.ATTR_CREATED_AT, ignore = true)
  @Mapping(target = User.ATTR_VERSION, ignore = true)
  @Mapping(target = User.ATTR_STATUS, ignore = true)
  @Mapping(target = User.ATTR_SALUTATION, ignore = true)
  @Mapping(target = User.ATTR_DISPLAY_NAME, ignore = true)
  @Mapping(target = User.ATTR_EMAIL, ignore = true)
  @Mapping(target = User.ATTR_USER_NAME, ignore = true)
  @Mapping(target = User.ATTR_FIRST_NAME, ignore = true)
  @Mapping(target = User.ATTR_LAST_NAME, ignore = true)
  @Mapping(target = User.ATTR_ROLES, ignore = true)
  @Mapping(target = User.ATTR_IMAGE_SRC, ignore = true)
  @Mapping(target = User.ATTR_PHONE_NUMBER, ignore = true)
  @Mapping(target = User.ATTR_IAAS_USERNAME, ignore = true)
  User fromDto(Long id);

  @Override
  @Mapping(target = User.ATTR_ROLE_BINDINGS, ignore = true)
  @Mapping(target = User.ATTR_ID, ignore = true)
  @Mapping(target = User.ATTR_LAST_UPDATED, ignore = true)
  @Mapping(target = User.ATTR_CREATED_AT, ignore = true)
  @Mapping(target = User.ATTR_VERSION, ignore = true)
  @Mapping(target = User.ATTR_STATUS, source = "statusId")
  @Mapping(target = User.ATTR_SALUTATION, source = "salutationId")
  @Mapping(target = User.ATTR_ROLES, source = "roleIds")
  @Mapping(target = User.ATTR_IAAS_USERNAME, ignore = true)
  User fromAddDto(AddUserDto addUserDto);

  @Override
  @Mapping(target = User.ATTR_ROLE_BINDINGS, ignore = true)
  @Mapping(target = User.ATTR_LAST_UPDATED, ignore = true)
  @Mapping(target = User.ATTR_CREATED_AT, ignore = true)
  @Mapping(target = User.ATTR_STATUS, source = "statusId")
  @Mapping(target = User.ATTR_SALUTATION, source = "salutationId")
  @Mapping(target = User.ATTR_ROLES, source = "roleIds")
  @Mapping(target = User.ATTR_IAAS_USERNAME, ignore = true)
  User fromUpdateDto(UpdateUserDto updateUserDto);

  @Override
  @Mapping(target = UserDto.ATTR_OBJECT_STORE_FILE, ignore = true)
  UserDto toDto(User user);
}
```
- **Key Annotations & Best Practices**:
    - `@Mapper(uses = {...})`: Injects other mappers that are required for mapping nested objects (e.g., mapping `UserStatus` to `UserStatusDto`).
    - **Use Static Constants for Targets**: Never specify target property names as raw string literals. Always reference static constant variables inherited from domain/DTO interfaces via the concrete target class (e.g., `@Mapping(target = User.ATTR_LAST_UPDATED, ignore = true)`).
    - **Mapping Nested ID Fields**: Avoid mapping nested ID fields using string concatenation or dot notation (e.g., `target = "chatModelConfig.id"`). Instead, list the dependent mapper in `uses = {...}` and map directly to the parent property (e.g., `@Mapping(target = AiAgentConfig.ATTR_CHAT_MODEL_CONFIG, source = "chatModelConfigId")`). MapStruct will automatically utilize the dependent mapper (which maps `Long` -> object with ID set) to handle the ID conversion.

## Implementation Guide

### 1. Database Migration
Create SQL migrations in `trishul-<domain>-service/src/main/resources/db/tenant_migrations/<domain>/`.
- Use `V1__base.sql` for the initial schema.
- Follow snake_case for table and column names.
- Use sequences for primary keys (e.g., `<ENTITY>_SEQUENCE`).

### 2. Entity Definition
Create the JPA entity in `trishul-<domain>/src/main/java/io/trishul/<domain>/model/`.
- Use JPA annotations: `@Entity`, `@Table(name = "_<entity>")`, `@Id`, `@GeneratedValue(strategy = GenerationType.SEQUENCE)`, `@Version`, `@CreationTimestamp`, `@UpdateTimestamp`.

### 3. Refresher Pattern
Create a `<Entity>Refresher` to resolve IDs into entities.
- Implements `Refresher<Entity, EntityAccessor<?>>`.
- Used to populate nested objects during service/mapper operations.

### 4. Repository & Service

The repository and service layers are the core of the business logic in a service module. The repository handles direct database interaction, while the service orchestrates operations, implements business rules, and coordinates between different components.

#### Repository Interface

The repository interface is the lowest level of data access. It should extend Spring Data JPA's `JpaRepository` and `JpaSpecificationExecutor` for standard CRUD and specification-based queries, as well as the framework's `ExtendedRepository`.

##### Repository Example

All custom repository methods, such as batch operations, should be defined in this interface.

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

#### Service Implementation

The service class contains the domain's business logic. It must implement the `CrudService` interface, which provides a standard contract for add, update, delete, and retrieve operations. The service coordinates with the repository (often via the generic `RepoService`), the `EntityMergerService`, and any other required services.

##### Service Example

The `UserService` below shows a typical implementation. It handles complex retrieval logic (`getUsers`), and orchestrates Iaas user management during add/update operations.

```java
package sh.trishul.user.service.user.service.service;

import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.SortedSet;
import java.util.stream.Collectors;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.data.jpa.domain.Specification;

import sh.trishul.base.types.base.pojo.Identified;
import sh.trishul.crud.service.BaseService;
import sh.trishul.crud.service.CrudService;
import sh.trishul.crud.service.EntityMergerService;
import sh.trishul.iaas.user.model.IaasUser;
import sh.trishul.iaas.user.model.IaasUserTenantMembership;
import sh.trishul.iaas.user.service.TenantIaasUserService;
import sh.trishul.model.base.exception.EntityNotFoundException;
import sh.trishul.repo.jpa.query.clause.where.builder.WhereClauseBuilder;
import sh.trishul.repo.jpa.repository.service.RepoService;
import sh.trishul.user.model.BaseUser;
import sh.trishul.user.model.UpdateUser;
import sh.trishul.user.model.User;
import sh.trishul.user.model.UserAccessor;
import sh.trishul.user.role.model.UserRole;
import sh.trishul.user.salutation.model.UserSalutation;
import sh.trishul.user.salutation.model.UserSalutationAccessor;
import sh.trishul.user.service.user.service.repository.UserRepository;
import sh.trishul.user.status.UserStatus;
import sh.trishul.user.status.UserStatusAccessor;
import jakarta.transaction.Transactional;

@Transactional
public class UserService extends BaseService
    implements CrudService<Long, User, BaseUser<?>, UpdateUser<?>, UserAccessor<?>> {
  private static final Logger log = LoggerFactory.getLogger(UserService.class);

  private final EntityMergerService<Long, User, BaseUser<?>, UpdateUser<?>> entityMergerService;
  private final RepoService<Long, User, UserAccessor<?>> repoService;
  private final UserRepository userRepo;
  private final TenantIaasUserService iaasService;

  public UserService(
      EntityMergerService<Long, User, BaseUser<?>, UpdateUser<?>> entityMergerService,
      RepoService<Long, User, UserAccessor<?>> repoService, UserRepository userRepo,
      TenantIaasUserService iaasService) {
    this.entityMergerService = entityMergerService;
    this.repoService = repoService;
    this.iaasService = iaasService;
    this.userRepo = userRepo;
  }

  public Page<User> getUsers(Set<Long> ids, Set<Long> excludeIds, Set<String> userNames,
      Set<String> displayNames, Set<String> emails, Set<String> phoneNumbers, Set<Long> statusIds,
      Set<Long> salutationIds, Set<String> roles, int page, int size, SortedSet<String> sort,
      boolean orderAscending) {
    final Specification<User> spec = WhereClauseBuilder.builder().in(User.ATTR_ID, ids).not()
        .in(User.ATTR_ID, excludeIds).in(User.ATTR_USER_NAME, userNames)
        .in(User.ATTR_DISPLAY_NAME, displayNames).in(User.ATTR_EMAIL, emails)
        .in(User.ATTR_PHONE_NUMBER, phoneNumbers)
        .in(new String[] {User.ATTR_STATUS, UserStatus.ATTR_ID}, statusIds)
        .in(new String[] {User.ATTR_SALUTATION, UserSalutation.ATTR_ID},
            salutationIds)
        .in(new String[] {User.ATTR_ROLES, UserRole.ATTR_ID}, roles).build();

    return this.repoService.getAll(spec, sort, orderAscending, page, size);
  }

  @Override
  public User get(Long id) {
    return this.repoService.get(id);
  }

  @Override
  public List<User> getByIds(Collection<? extends Identified<Long>> idProviders) {
    return this.repoService.getByIds(idProviders);
  }

  @Override
  public List<User> getByAccessorIds(Collection<? extends UserAccessor<?>> accessors) {
    return this.repoService.getByAccessorIds(accessors, UserAccessor::getUser);
  }

  @Override
  public boolean exists(Set<Long> ids) {
    return this.repoService.exists(ids);
  }

  @Override
  public boolean exist(Long id) {
    return this.repoService.exists(id);
  }

  @Override
  public long delete(Set<Long> ids) {
    List<User> users = this.userRepo.findAllById(ids);
    long deleteCount = this.repoService.delete(ids);
    long iaasUserDeleteResult = this.iaasService.delete(users);
    log.info("Deleted users: {}", iaasUserDeleteResult);

    return deleteCount;
  }

  @Override
  public long delete(Long id) {
    return this.delete(Set.of(id));
  }

  @Override
  public List<User> add(final List<? extends BaseUser<?>> additions) {
    if (additions == null) {
      return null;
    }

    final List<User> entities = this.entityMergerService.getAddEntities(additions);

    List<User> users = this.repoService.saveAll(entities);

    List<IaasUserTenantMembership> updatedIaasUserMemberships = this.iaasService.put(users);

    // Create a map of email to IaasUser for efficient lookup
    Map<String, IaasUser> iaasUserMap = updatedIaasUserMemberships.stream()
        .map(IaasUserTenantMembership::getUser).filter(Objects::nonNull)
        .collect(Collectors.toMap(IaasUser::getId, iaasUser -> iaasUser));

    // Update users with IaasUsername
    users.forEach(user -> {
      IaasUser iaasUser = iaasUserMap.get(user.getEmail());
      if (iaasUser != null) {
        user.setIaasUsername(iaasUser.getUserName());
      }
    });

    users = this.repoService.saveAll(users);

    log.info("Added users: {}", users.size());

    return users;
  }

  @Override
  public List<User> put(List<? extends UpdateUser<?>> updates) {
    if (updates == null) {
      return null;
    }

    final List<User> existing = this.repoService.getByIds(updates);
    final List<User> updated = this.entityMergerService.getPutEntities(existing, updates);

    List<IaasUserTenantMembership> updatedIaasUserMemberships = this.iaasService.put(updated);

    Map<String, IaasUser> iaasUserMap = updatedIaasUserMemberships.stream()
        .map(IaasUserTenantMembership::getUser).filter(Objects::nonNull)
        .collect(Collectors.toMap(IaasUser::getId, iaasUser -> iaasUser));

    updated.forEach(user -> {
      IaasUser iaasUser = iaasUserMap.get(user.getEmail());
      if (iaasUser != null) {
        user.setIaasUsername(iaasUser.getUserName());
      }
    });

    List<User> users = this.repoService.saveAll(updated);

    return users;
  }

  @Override
  public List<User> patch(List<? extends UpdateUser<?>> patches) {
    if (patches == null) {
      return null;
    }

    final List<User> existing = this.repoService.getByIds(patches);

    if (existing.size() != patches.size()) {
      final Set<Long> existingIds
          = existing.stream().map(Identified::getId).collect(Collectors.toSet());
      final Set<Long> nonExistingIds = patches.stream().map(Identified::getId)
          .filter(patchId -> !existingIds.contains(patchId)).collect(Collectors.toSet());

      throw new EntityNotFoundException(
          String.format("Cannot find users with Ids: %s", nonExistingIds));
    }

    final List<User> updated = this.entityMergerService.getPatchEntities(existing, patches);

    return this.repoService.saveAll(updated);
  }
}
```

### 5. Controller Definition

All REST controllers must follow a standardized pattern to ensure consistency and leverage the `trishul-crud` framework. The primary component for this is the `CrudControllerService`, which handles the boilerplate logic for GET, POST, PUT, PATCH, and DELETE operations.

#### Controller Template

New controllers should be modeled after the following `UserController` example. This structure provides a consistent API surface for all domain entities.

```java
package sh.trishul.user.service.user.service.controller;

import sh.trishul.crud.controller.BaseController;
import sh.trishul.crud.controller.CrudControllerService;
import sh.trishul.crud.controller.filter.AttributeFilter;
import sh.trishul.repo.jpa.repository.model.dto.PageDto;
import sh.trishul.user.model.AddUserDto;
import sh.trishul.user.model.BaseUser;
import sh.trishul.user.model.UpdateUser;
import sh.trishul.user.model.UpdateUserDto;
import sh.trishul.user.model.User;
import sh.trishul.user.model.UserDto;
import sh.trishul.user.model.UserMapper;
import sh.trishul.user.service.user.service.service.UserService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;
import java.util.List;
import java.util.Set;
import java.util.SortedSet;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping(path = "/api/v1/users")
public class UserController extends BaseController {
  private final CrudControllerService<Long, User, BaseUser<?>, UpdateUser<?>, UserDto, AddUserDto, UpdateUserDto> controller;

  private final UserService userService;

  protected UserController(
      CrudControllerService<Long, User, BaseUser<?>, UpdateUser<?>, UserDto, AddUserDto, UpdateUserDto> controller,
      UserService userService) {
    this.controller = controller;
    this.userService = userService;
  }

  @Autowired
  public UserController(UserService userService, AttributeFilter filter,
      UserDtoDecorator decorator) {
    this(new CrudControllerService<>(filter, UserMapper.INSTANCE, userService, "User", decorator),
        userService);
  }

  @GetMapping(value = "", consumes = MediaType.ALL_VALUE,
      produces = MediaType.APPLICATION_JSON_VALUE)
  public PageDto<UserDto> getAllUsers(@RequestParam(required = false) Set<Long> ids,
      @RequestParam(required = false, name = "exclude_ids") Set<Long> excludeIds,
      @RequestParam(required = false, name = "user_names") Set<String> userNames,
      @RequestParam(required = false, name = "display_names") Set<String> displayNames,
      @RequestParam(required = false, name = "emails") Set<String> emails,
      @RequestParam(required = false, name = "phone_numbers") Set<String> phoneNumbers,
      @RequestParam(required = false, name = "status") Set<Long> statusIds,
      @RequestParam(required = false, name = "salutations") Set<Long> salutationIds,
      @RequestParam(required = false, name = "roles") Set<String> roles,
      @RequestParam(name = PROPNAME_SORT_BY,
          defaultValue = VALUE_DEFAULT_SORT_BY) SortedSet<String> sort,
      @RequestParam(name = PROPNAME_ORDER_ASC,
          defaultValue = VALUE_DEFAULT_ORDER_ASC) boolean orderAscending,
      @RequestParam(name = PROPNAME_PAGE_INDEX, defaultValue = VALUE_DEFAULT_PAGE_INDEX) int page,
      @RequestParam(name = PROPNAME_PAGE_SIZE, defaultValue = VALUE_DEFAULT_PAGE_SIZE) int size,
      @RequestParam(name = PROPNAME_ATTR,
          defaultValue = VALUE_DEFAULT_ATTR) Set<String> attributes) {
    Page<User> userPage = userService.getUsers(ids, excludeIds, userNames, displayNames, emails,
        phoneNumbers, statusIds, salutationIds, roles, page, size, sort, orderAscending);

    return this.controller.getAll(userPage, attributes);
  }

  @GetMapping(value = "/{userId}", consumes = MediaType.ALL_VALUE,
      produces = MediaType.APPLICATION_JSON_VALUE)
  public UserDto getUser(@PathVariable(required = true, name = "userId") Long userId,
      @RequestParam(name = PROPNAME_ATTR,
          defaultValue = VALUE_DEFAULT_ATTR) Set<String> attributes) {
    return this.controller.get(userId, attributes);
  }

  @DeleteMapping(value = "", consumes = MediaType.ALL_VALUE)
  @ResponseStatus(value = HttpStatus.ACCEPTED)
  public long deleteUsers(@RequestParam("ids") Set<Long> userIds) {
    return this.controller.delete(userIds);
  }

  @PostMapping(value = "", consumes = MediaType.APPLICATION_JSON_VALUE,
      produces = MediaType.APPLICATION_JSON_VALUE)
  @ResponseStatus(value = HttpStatus.CREATED)
  public List<UserDto> addUser(@Valid @NotNull @RequestBody List<AddUserDto> addDtos) {
    return this.controller.add(addDtos);
  }

  @PutMapping(value = "", consumes = MediaType.APPLICATION_JSON_VALUE,
      produces = MediaType.APPLICATION_JSON_VALUE)
  @ResponseStatus(value = HttpStatus.ACCEPTED)
  public List<UserDto> updateUser(@Valid @NotNull @RequestBody List<UpdateUserDto> updateDtos) {
    return this.controller.put(updateDtos);
  }

  @PatchMapping(value = "", consumes = MediaType.APPLICATION_JSON_VALUE,
      produces = MediaType.APPLICATION_JSON_VALUE)
  @ResponseStatus(value = HttpStatus.ACCEPTED)
  public List<UserDto> patchUser(@Valid @NotNull @RequestBody List<UpdateUserDto> updateDtos) {
    return this.controller.patch(updateDtos);
  }
}
```

#### Key Components
- **`@RestController`**: Marks the class as a Spring REST controller.
- **`@RequestMapping`**: Defines the base path for the API (e.g., `/api/v1/users`).
- **`CrudControllerService`**: A generic service that encapsulates all standard CRUD logic. It is initialized with the domain's `Mapper`, `Service`, and an `AttributeFilter`.
- **`@GetMapping (Paged)`**: The main endpoint for fetching a paginated and filtered list of entities. Note how it delegates directly to the domain `Service` for complex queries and then passes the result to `controller.getAll()` for DTO conversion and attribute filtering.
- **Standard CRUD Methods**: `getUser`, `deleteUsers`, `addUser`, `updateUser`, and `patchUser` are thin wrappers that delegate directly to the corresponding methods in `CrudControllerService`.

### 5a. DTO Decorators

Decorators provide a mechanism to enrich DTOs with additional, often transient, data before they are returned by the controller. This is useful for adding data that is not part of the core entity, such as generating temporary URLs for images.

Decorators implement the `EntityDecorator<T>` interface and are injected into the `CrudControllerService` via the controller's constructor.

#### Decorator Example

The `UserDtoDecorator` below uses a `TemporaryImageSrcDecorator` to add a temporary image URL to the `UserDto`.

```java
package sh.trishul.user.service.user.service.controller;

import sh.trishul.object.store.file.decorator.EntityDecorator;
import sh.trishul.object.store.file.service.decorator.TemporaryImageSrcDecorator;
import sh.trishul.user.model.UserDto;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class UserDtoDecorator implements EntityDecorator<UserDto> {
  @SuppressWarnings("unused")
  private static final Logger log = LoggerFactory.getLogger(UserDtoDecorator.class);

  private TemporaryImageSrcDecorator imageSrcDecorator;

  public UserDtoDecorator(TemporaryImageSrcDecorator imageSrcDecorator) {
    this.imageSrcDecorator = imageSrcDecorator;
  }

  @Override
  public <R extends UserDto> void decorate(List<R> entities) {
    this.imageSrcDecorator.decorate(entities);
  }
}
```

### 6. Autoconfiguration

To make the service module available to the main application, you must create an autoconfiguration class. This class is responsible for discovering and manually wiring all the necessary beans for the domain, such as services, repositories, mergers, and refreshers. This ensures that the generic framework components are correctly typed and instantiated for the specific domain.

#### Autoconfiguration Example

The `UserServiceAutoConfiguration` class below is a complete example of how to wire the entire `user` domain. It should be placed in the `...<domain>.service.autoconfiguration` package.

```java
package sh.trishul.user.service.user.service.autoconfiguration;

import java.util.Set;

import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Lazy;

import sh.trishul.auth.session.context.holder.ContextHolder;
import sh.trishul.base.types.base.pojo.OwnedByAccessor;
import sh.trishul.base.types.base.pojo.Refresher;
import sh.trishul.crud.service.CrudEntityMergerService;
import sh.trishul.crud.service.CrudRepoService;
import sh.trishul.crud.service.EntityMergerService;
import sh.trishul.crud.service.LockService;
import sh.trishul.iaas.user.service.TenantIaasUserService;
import sh.trishul.model.base.pojo.refresher.accessor.AccessorRefresher;
import sh.trishul.object.store.file.service.decorator.TemporaryImageSrcDecorator;
import sh.trishul.repo.jpa.repository.service.RepoService;
import sh.trishul.user.model.AssignedToAccessor;
import sh.trishul.user.model.BaseUser;
import sh.trishul.user.model.UpdateUser;
import sh.trishul.user.model.User;
import sh.trishul.user.model.UserAccessor;
import sh.trishul.user.model.UserRefresher;
import sh.trishul.user.role.binding.model.UserRoleBinding;
import sh.trishul.user.role.binding.model.UserRoleBindingAccessor;
import sh.trishul.user.role.binding.model.UserRoleBindingRefresher;
import sh.trishul.user.role.model.BaseUserRole;
import sh.trishul.user.role.model.UpdateUserRole;
import sh.trishul.user.role.model.UserRole;
import sh.trishul.user.role.model.UserRoleAccessor;
import sh.trishul.user.role.model.UserRoleRefresher;
import sh.trishul.user.salutation.model.UserSalutation;
import sh.trishul.user.salutation.model.UserSalutationAccessor;
import sh.trishul.user.salutation.model.UserSalutationRefresher;
import sh.trishul.user.service.user.service.controller.UserDtoDecorator;
import sh.trishul.user.service.user.service.repository.UserRepository;
import sh.trishul.user.service.user.service.repository.role.repository.UserRoleRepository;
import sh.trishul.user.service.user.service.role.service.UserRoleService;
import sh.trishul.user.service.user.service.salutation.repository.UserSalutationRepository;
import sh.trishul.user.service.user.service.salutation.service.UserSalutationService;
import sh.trishul.user.service.user.service.service.AccountService;
import sh.trishul.user.service.user.service.service.UserService;
import sh.trishul.user.service.user.service.status.repository.UserStatusRepository;
import sh.trishul.user.status.UserStatus;
import sh.trishul.user.status.UserStatusAccessor;
import sh.trishul.user.status.UserStatusRefresher;

@Configuration
public class UserServiceAutoConfiguration {
  @Bean @ConditionalOnMissingBean(UserService.class)
  public UserService userService(LockService lockService, UserRepository userRepository,
      Refresher<User, UserAccessor<?>> userRefresher, TenantIaasUserService tenantIaasUserService) {
    final EntityMergerService<Long, User, BaseUser<?>, UpdateUser<?>> updateService
        = new CrudEntityMergerService<>(lockService, BaseUser.class, UpdateUser.class, User.class,
            Set.of());
    final RepoService<Long, User, UserAccessor<?>> repoService
        = new CrudRepoService<>(userRepository, userRefresher);
    return new UserService(updateService, repoService, userRepository, tenantIaasUserService);
  }

  @Bean @ConditionalOnMissingBean(UserDtoDecorator.class)
  public UserDtoDecorator userDecorator(TemporaryImageSrcDecorator imgDecorator) {
    return new UserDtoDecorator(imgDecorator);
  }

  @Bean
  public AccessorRefresher<Long, UserAccessor<?>, User> userAccessorRefresher(UserRepository repo) {
    return new AccessorRefresher<>(User.class, UserAccessor::getUser,
        (accessor, user) -> accessor.setUser(user), ids -> repo.findAllById(ids));
  }

  @Bean
  public AccessorRefresher<Long, AssignedToAccessor<?>, User> assignedToAccessorRefresher(
      UserRepository repo) {
    return new AccessorRefresher<>(User.class, AssignedToAccessor::getAssignedTo,
        (accessor, assignedTo) -> accessor.setAssignedTo(assignedTo), ids -> repo.findAllById(ids));
  }

  @Bean
  public AccessorRefresher<Long, OwnedByAccessor<User>, User> ownedByAccessorRefresher(
      UserRepository repo) {
    return new AccessorRefresher<>(User.class, OwnedByAccessor::getOwnedBy,
        (accessor, ownedBy) -> accessor.setOwnedBy(ownedBy), ids -> repo.findAllById(ids));
  }

  @Bean
  public UserRefresher userRefresher(
      AccessorRefresher<Long, UserAccessor<?>, User> userAccessorRefresher,
      AccessorRefresher<Long, AssignedToAccessor<?>, User> assignedToAccessorRefresher,
      AccessorRefresher<Long, OwnedByAccessor<User>, User> ownedByAccessorRefresher,
      Refresher<UserStatus, UserStatusAccessor<?>> statusRefresher,
      Refresher<UserSalutation, UserSalutationAccessor<?>> salutationRefresher,
      @Lazy Refresher<UserRoleBinding, UserRoleBindingAccessor<?>> roleBindingRefresher) {
    return new UserRefresher(userAccessorRefresher, assignedToAccessorRefresher,
        ownedByAccessorRefresher, statusRefresher, salutationRefresher, roleBindingRefresher);
  }
}
```

#### Key Bean Definitions
- **Service Bean**: The `userService` bean constructs the main `UserService`. It programmatically creates its dependencies, `CrudEntityMergerService` and `CrudRepoService`, and injects them.
- **Decorator Bean**: The `userDecorator` bean provides the `UserDtoDecorator` used by the controller.
- **Refresher Beans**: A series of `AccessorRefresher` beans are defined to handle refreshing different entity relationships (e.g., `assignedTo`, `ownedBy`). These are then composed into a single `UserRefresher` bean, which is injected into the `repoService`. This pattern is central to resolving nested objects efficiently.
- **`@ConditionalOnMissingBean`**: This annotation ensures that these default beans are only created if a bean of the same type has not already been defined elsewhere, allowing for easy customization and overriding.

#### Autoconfiguration & dependency-injection conventions (add to the above pattern)
- **Do not annotate domain services with `@Service`/`@Component`.** Domain services are plain classes registered as `@Bean`s in the per-domain autoconfiguration (as above). This keeps bean wiring explicit and overridable via `@ConditionalOnMissingBean`. Audit entity listeners and their configurers are also registered as beans here rather than `@Component`, because Hibernate instantiates `@EntityListeners` directly.
- **Current user**: read from `sh.trishul.auth.session.context.holder.ContextHolder` (`contextHolder.getPrincipalContext().getUsername()`), NOT Spring's `SecurityContextHolder`. Inject the `ContextHolder` bean into the service constructor (a `ThreadLocalContextHolder` impl is provided by `AuthAutoConfiguration`).
- **JSON serialization**: use `sh.trishul.model.json.JsonMapper.INSTANCE.writeString(...)` (a static `INSTANCE`; not a Spring bean) instead of hand-rolling an `ObjectMapper` with a `JavaTimeModule`.
- **Entity decorators**: call the injected decorator unconditionally — skip redundant `entities != null && !entities.isEmpty()` guards; the internal decorator already handles empty input.
- **Free-text search**: `RepoService` provides a `default Page<E> search(String query, String[][] fieldPaths, SortedSet<String> sort, boolean orderAscending, int page, int size)` that tokenizes the query (AND across terms, OR across field paths) using an `ilike` predicate. Prefer delegating domain `getXxx(.../*search*/...)` methods to `repoService.search(...)` instead of re-implementing tokenize/OR/AND loops manually.


## Naming & Style Conventions
- **Reserved Words**: Prefix table names with `_` if they are SQL reserved words (e.g., `_USER`).
- **Generic Typing**: Interfaces should use recursive generics: `<T extends BaseEntity<T>>`.
- **Validation**: Use Jakarta Validation (`@NotBlank`, `@NotNull`) and custom Trishul validators (`@NullOrNotBlank`).

## Troubleshooting & Common Build Issues

When developing in the Trishul framework, keep these common patterns and fixes in mind to avoid build failures:

### 1. Custom JPA Methods in Repositories
Any repository interface extending `ExtendedRepository` must provide explicit `@Query` and `@Modifying` overrides for methods like `existsByIds` and `deleteByIds` to satisfy Spring Data's repository factory.
Example:
```java
@Override
@Modifying
@Query("delete from entity_name e where e.id in :ids")
long deleteByIds(@Param("ids") Collection<Long> ids);

@Override
@Query("select count(e) > 0 from entity_name e where e.id in :ids")
boolean existsByIds(@Param("ids") Collection<Long> ids);
```

### 2. Configuration Imports for Auto-configuration
If you add new auto-configuration modules that provide required environment variables, ensure they are imported in `trishul-app` tests.
Add `classpath:module-name-application.properties` to the `spring.config.import` property in `trishul-app/src/test/resources/application.properties` (and `application-test.properties`). Missing imports typically result in `PlaceholderResolutionException` during application startup in tests.

### 3. Application Class in Test-Scope
If a module (e.g., `trishul-app` or a parent app module) only contains its `Application.java` in the test-scope (for testing application startup), you must configure the `spring-boot-maven-plugin` to skip execution in its `pom.xml`. Otherwise, the plugin will attempt to package a non-existent main class or fail during the repackage phase.
```xml
<plugin>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-maven-plugin</artifactId>
    <configuration>
        <skip>true</skip>
    </configuration>
</plugin>
```
