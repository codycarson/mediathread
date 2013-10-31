# Changelog

### 0.2.6

* completely disable smoke tests so that the Travis CI build doesn't fail

### 0.2.5

* increased the length of organization name field to 100
* fixed the bug where user profiles weren't created for newly invited users

### 0.2.1 - 0.2.4

* bugfixes

### 0.2.0
* user profiles added
* improved call to action bars
* integrated upstream changes from release [v2013_Fall.3](https://github.com/ccnmtl/mediathread/releases/tag/v2013_Fall.3)

### 0.1.2 - 0.1.6

* bugfixes

### 0.1.1

* fixed absolute paths to static files in mediathread.css to be
  compatible with S3

### 0.1

* static files server used Amazon S3 ([#137](https://trello.com/c/03Y3xdxx/137-use-django-storages-to-send-all-static-assets-to-s3))
* added welcome screen for newly registered users ([#146](https://trello.com/c/nkMlxRXq/146-optional-enrolling-to-sample-course))
* fixed sending the correct user type to segment.io ([#148](https://trello.com/c/iNPBSDkh/148-fix-sending-the-user-type-to-segment-io))
* new users have the option of joining the sample course only as students
