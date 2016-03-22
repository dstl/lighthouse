# lighthouse
Web application for finding useful tools, data and techniques

## Install & run

### On a Virtual Machine (recommended)

  1. Head to [dstl-infrastructure](https://github.com/livestax/dstl-infrastructure)
  2. Follow the instructions to set up the virtual machine (VM)
  3. Run `vagrant ssh` to `ssh` onto the VM
  4. `cd /opt/lighthouse` and you'll be in the NFS-mounted folder which you
  pointed the VM to with the `DSTL_LIGHTHOUSE` environment variable on your
  machine.
  5. Create a virtual environment (env) using `virtualenv ~/lighthouse` or whatever
  directory you prefer to store the environment
  6. Load the env using `source ~/lighthouse/bin/activate` - you should now see
  `(env)` at the start of your prompt.
  7. Install the Python dependencies using `pip install -r requirements.txt`
  8. Migrate the database using `python manage.py migrate` (Postgres will be
      running already)
  9. Run the server using `python manage.py runserver 0.0.0.0:3000` or whatever
  port you prefer, as long as the same IP is used.
  10. In your web browser, navigate to http://10.10.11.10:3000 (or http://lighthouse.dev:3000 if your
      hosts file is set up for this)
  11. You should see the Lighthouse homepage.

### Run the tests

    pip install -r requirements_test.txt

    ./manage.py test

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
