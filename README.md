# lighthouse
Web application for finding useful tools, data and techniques

## Install & run

### On a Virtual Machine (recommended)

  1. Head to [dstl-infrastructure](/digi2al/dstl-infrastructure)
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
  10. In your web browser, navigate to 10.10.11.10:3000 (or `lighthouse.dev` if your
      hosts file is set up for this)
  11. You should see the Lighthouse homepage.
