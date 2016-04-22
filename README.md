# Lighthouse

Lighthouse is a web application for finding tools and sharing data about how those tools are used. You can use it to manage a searchable and collaboratively curated catalog of internal (eg intranet) and/or external (eg internet) links to useful tools. It also helps you see which people, teams and organisations are using which tools.

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

To run all of the tests:

    ./bin/test.sh

To run an individual test (or test class) in isolation, run:

    # eg. just run all the Link model tests
    ./manage.py test apps.links.tests.test_model

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

### How does it look?

It should look a little bit like this:

![A screenshot of Lighthouse](../master/readme.png?raw=true)


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

## How to modify static assets

Lighthouse contains some "static" content assets which are not generated at
runtime in the sense that a user's detail page is generated at runtime. The
types of static content are images and pages, and sometimes you'll need to
change them.

### Modifying images

At the time of this writing there's onyl one image being used in Lighthouse, and
that's the logo which appears in the top-left of the page. This logo is
originally stored in the `lighthouse-secrets` repository in a folder called
`<nameofenvironment>-assets` (for example `preview-assets`) as `logo.png`. If
you want to change the image for any of the environments, find the appropriate
folder in the `lighthouse-secrets` repo and replace the image. It should be
updated when you next deploy.

### Modifying pages

At time of writing there are two pieces of static text content on the Lighthouse
site: the "About" page and the "API Documentation" page.

The About page is the most straightforward. In the `apps/staticpages/pages/`
directory there's a file called `about.md`. This is a Markdown file. If you
aren't familiar with it, Markdown is a simple text format which renders to HTML.
It is inspired by 1990s plain-text email convention and in fact, even if you
simply write plain text, Markdown will render nicely to HTML. Here's some
Markdown:

```
# This is a header

This is a paragraph.

Another paragraph.

## A smaller header.

Another paragraph!
```

You get the picture. More information is available on the [Markdown Syntax
Documentation Page](https://daringfireball.net/projects/markdown/syntax).

The about page is located at /about because of the name of that Markdown file.
If you put another one in that directory called `contact.md`, then the URL
/contact would suddenly become whatever is in that file, rendered as HTML.

The *API Documentation* pages are a little more complicated but still fairly
straightforward to change. The directory `apps/api/documentation` contains some
markdown files which become available in their HTML-rendered form at /api/docs/,
where `index.md` is the file which appears when you use just that path. On the
other hand, /api/docs/link-usage is generated from the `link-usage.md` file.

So as you can probably tell, to create a new page such as /api/docs/user-usage,
you'd create a new file called `user-usage.md` inside of
`apps/api/documentation`.

### Advanced static pages modification

The files in `apps/staticpages/pages/` are turned into HTML pages by using the
`StaticPageViewBase` class in `apps/staticpages/views.py`. The URLs are configured
in `lighthouse/urls.py`.

The API documentation pages merely extend the `StaticPageViewBase` class in
`apps/api/views.py`, so you could do something like that to start serving static
pages from a new directory if you like.
