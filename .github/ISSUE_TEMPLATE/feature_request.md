---
name: Feature request
about: Suggest an idea for this project
title: ''
labels: ''
assignees: ''

---

**Is your feature request related to an existing tool?**

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is.

**Describe the solution you'd like**
A clear and concise description of what you want to happen.
Example using Gherkin syntax:

```Gherkin
Feature: BVH to FBX File Conversion

  So that I can use animation in my Unity projects
  As a tech-artist
  I want to convert BVH files to FBX format

  Background:
    Given the following conversion rules:
      | Rule                              | Example                                                        |
      | The FBX file should be created    | An FBX file named "example.fbx" should be created              |
      | The FBX file should contain data  | The FBX file should contain the same animation data as the BVH |

  Scenario: Convert BVH file to FBX file
    Given a BVH file "example.bvh" exists
    When I convert the BVH file to FBX format
    Then the following rules should be met:
      | Rule                              |
      | The FBX file should be created    |
      | The FBX file should contain data  |
      And an FBX file named "example.fbx" should be created

  Scenario: Reject non-existent BVH file
    Given a non-existent BVH file "nonexistent.bvh"
    When I attempt to convert the BVH file to FBX format
    Then no FBX file should be created
    And I see an error message "BVH file not found"
  ...
```

But you can also write a free-form description.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
