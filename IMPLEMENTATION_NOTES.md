## photo-processor exercise implementation

### About

This is working, but not ultimate solution for this task.
It does not include automatic tests, cause writing tests for asynchronous system is
kind complicated and I not sure it's nice idea to spend a lot of time for tests for
this exercise.
If you have some ideas how to test this code properly, please say me, I'm really interested
in!



### How to run it.
- Just setup a docker as README says.
- Populate db as README says
and use extra commands.
- `make list_pending` to get result of `GET /photos/pending`
- `make process` to process all pending photos
- `make show_data` to see `photos` and `photos_thumbnails` tables and list of thumbnails
  files

after all should be 5 thumbnails records and files
