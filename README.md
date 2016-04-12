# lighthouse Web application for finding useful tools, data and techniques

## Install & run

### On a Virtual Machine (recommended)

  1. Head to [dstl-infrastructure](https://github.com/dstl/lighthouse-builder)
  2. Follow the instructions to set up the virtual machine (VM)
  3. Run `vagrant ssh` to `ssh` onto the VM
  4. `cd /opt/lighthouse` and you'll be in the NFS-mounted folder which you
  pointed the VM to with the `DSTL_LIGHTHOUSE` environment variable on your
  machine.
  5. Create and activate a virtual environment (env) using
  `source ./bin/virtualenv.sh`
  6. Install the Python dependencies using `pip install -r requirements.txt` and `pip install -r requirements_test.txt`
  7. Migrate the database using `python manage.py migrate` (Postgres will be
  running already)
  8. Run the server using `python manage.py runserver 0.0.0.0:3000` or whatever
  port you prefer, as long as the same IP is used.
  9. In your web browser, navigate to http://10.10.11.10:3000
  10. You should see the Lighthouse homepage.

### _Not_ on a Virtual Machine (not recommended)

The steps are the same as above ("On a Virtual Machine") except that they start
at step **5** and the IP address in the end will be https://0.0.0.0:3000.

### Run the tests

    pip install -r requirements_test.txt

    ./manage.py test

### Useful scripts in the `bin` directory

The `bin` directory of this repository contains some useful scripts for
performing common tasks related to Lighthouse development or deployment.

You will see some common lines in these scripts, such as `. ./bin/virtualenv.sh`
which is usually used at the beginning to ensure that the shell is in the
correct virtual environment. Some scripts will use other scripts in the same
directory, too.

`acceptance-test.sh` will run the acceptance test suite, which ensures that the
application has been successfully deployed to some accessible environment. This
is used by Jenkins in its "Acceptance Test" job.

`addcopyright.sh` ensures that a DSTL Copyright comment is present at the top of
all proprietary code within the repository. You may run it whenever you have
created a new file before pushing the file to the remote repo.

`deploy.sh` will run the deploy-related commands including migrating the
database, rebuilding the search index, compressing static assets (such as SCSS →
CSS and disjointed JS → compiled and compressed JS), and finally collecting
static assets into a folder from where they are to be served.

`jenkins.sh` is intended to be run by Jenkins against a branch to ensure that it
has 'passed'. This includes running all the tests (excl. acceptance) and doing a
pep8 style check using `style.sh`.

`pip-download.sh` will make sure Python dependencies are downloaded to somewhere
local as long as Internet access is available.

`pip-install.sh` will install the Python dependencies downloaded by
`pip-download.sh`. These two scripts work together as part of the process of
installing Lighthouse onto an offline environment.

`style.sh` runs a pep8 style check against the entire Python codebase. It may
need to be edited when build-in globals are added to the codebase, e.g. with
`FileNotFoundError`

`test.sh` runs all the tests excluding acceptance tests.

`virtualenv.sh` will create a virtual environment for the app to store
dependencies, and will also return the location of that environment's `activate`
binary. So in order to quickly get into a virtual environment you can type
`source ./bin/virtualenv.sh`.

### API

Lighthouse provides a (very) limited RESTful API. The documentation can be
found in the repo under `apps/api/documentation` and linked from the footer
in a running instance of the lighthouse code.

## Backup and restore

All data in a running lighthouse instance is kept in PostgreSQL. To back up
the data, on the database machine run:

    pg_dump lighthouse > backup.`date +%F`.sql

Don't forget to move the backup file off the machine.

If/when you need to restore the database from a backup, copy the most recent
backup file onto the database machine, and run:

    psql lighthouse < backup.*.sql

With both commands, if you have overridden the database name (using the
`LIGHTHOUSE_DB` environment variable), you will need to replace `lighthouse`
with that.
