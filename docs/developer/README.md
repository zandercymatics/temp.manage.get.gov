# Development
========================

If you're new to Django, see [Getting Started with Django](https://www.djangoproject.com/start/) for an introduction to the framework.

## Local Setup

* Install Docker <https://docs.docker.com/get-docker/>
* Initialize the application:

  ```shell
  cd src
  docker-compose build
  ```
* Run the server: `docker-compose up`

  Press Ctrl-c when you'd like to exit or pass `-d` to run in detached mode.

Visit the running application at [http://localhost:8080](http://localhost:8080).


### Troubleshooting 

* If you are using Windows, you may need to change your [line endings](https://docs.github.com/en/get-started/getting-started-with-git/configuring-git-to-handle-line-endings). If not, you may not be able to run manage.py. 
* Unix based operating systems (like macOS or Linux) handle line separators [differently than Windows does](https://superuser.com/questions/374028/how-are-n-and-r-handled-differently-on-linux-and-windows). This can break bash scripts in particular. In the case of manage.py, it uses *#!/usr/bin/env python* to access the Python executable. Since the script is still thinking in terms of unix line seperators, it may look for the executable *python\r* rather than *python* (since Windows cannot read the carriage return on its own) - thus leading to the error `usr/bin/env: 'python\r' no such file or directory` 
* If you'd rather not change this globally, add a `.gitattributes` file in the project root with `* text eol=lf` as the text content, and [refresh the repo](https://docs.github.com/en/get-started/getting-started-with-git/configuring-git-to-handle-line-endings#refreshing-a-repository-after-changing-line-endings)
* If you are using a Mac with a M1 chip, and see this error `The chromium binary is not available for arm64.` or an error involving `puppeteer`, try adding this line below into your `.bashrc` or `.zshrc`. 

```
export DOCKER_DEFAULT_PLATFORM=linux/amd64
```

When completed, don't forget to rerun `docker-compose up`! 

## Branch Conventions

We use the branch convention of `initials/branch-topic` (ex: `lmm/fix-footer`). This allows for automated deployment to a developer sandbox namespaced to the initials.

## Merging and PRs

History preservation and merge contexts are more important to us than a clean and linear history, so we will merge instead of rebasing. 
To bring your feature branch up-to-date wih main:

```
git checkout main
git pull
git checkout <feature-branch>
git merge orgin/main
git push
```

Resources:
- [https://frontend.turing.edu/lessons/module-3/merge-vs-rebase.html](https://frontend.turing.edu/lessons/module-3/merge-vs-rebase.html)
- [https://www.atlassian.com/git/tutorials/merging-vs-rebasing](https://www.atlassian.com/git/tutorials/merging-vs-rebasing)
- [https://www.simplilearn.com/git-rebase-vs-merge-article](https://www.simplilearn.com/git-rebase-vs-merge-article)

## Setting Vars

Non-secret environment variables for local development are set in [src/docker-compose.yml](../../src/docker-compose.yml).

Secrets (for example, if you'd like to have a working Login.gov authentication) go in `.env` in [src/](../../src/) with contents like this:

```
DJANGO_SECRET_LOGIN_KEY="<...>"
```

You'll need to create the `.env` file yourself. Get started by running:

```shell
cd src
cp ./.env-example .env
```

Get the secrets from Cloud.gov by running `cf env getgov-YOURSANDBOX`. More information is available in [rotate_application_secrets.md](../operations/runbooks/rotate_application_secrets.md).

## Adding user to /admin

The endpoint /admin can be used to view and manage site content, including but not limited to user information and the list of current applications in the database. To be able to view and use /admin locally:

1. Login via login.gov
2. Go to the home page and make sure you can see the part where you can submit an application
3. Go to /admin and it will tell you that UUID is not authorized, copy that UUID for use in 4
4. in src/registrar/fixtures_users.py add to the `ADMINS` list in that file by adding your UUID as your username along with your first and last name. See below:

```
 ADMINS = [
        {
            "username": "<UUID here>",
            "first_name": "",
            "last_name": "",
        },
        ...
 ]
```

5. In the browser, navigate to /admin. To verify that all is working correctly, under "domain applications" you should see fake domains with various fake statuses.
6. Add an optional email key/value pair

### Adding an Analyst to /admin
Analysts are a variant of the admin role with limited permissions. The process for adding an Analyst is much the same as adding an admin:

1. Login via login.gov (if you already exist as an admin, you will need to create a separate login.gov account for this: i.e. first.last+1@email.com)
2. Go to the home page and make sure you can see the part where you can submit an application
3. Go to /admin and it will tell you that UUID is not authorized, copy that UUID for use in 4 (this will be a different UUID than the one obtained from creating an admin)
4. in src/registrar/fixtures_users.py add to the `STAFF` list in that file by adding your UUID as your username along with your first and last name. See below:

```
 STAFF = [
        {
            "username": "<UUID here>",
            "first_name": "",
            "last_name": "",
        },
        ...
 ]
```

5. In the browser, navigate to /admin. To verify that all is working correctly, verify that you can only see a sub-section of the modules and some are set to view-only.
6. Add an optional email key/value pair

Do note that if you wish to have both an analyst and admin account, append `-Analyst` to your first and last name, or use a completely different first/last name to avoid confusion. Example: `Bob-Analyst`
## Adding to CODEOWNERS (optional)

The CODEOWNERS file sets the tagged individuals as default reviewers on any Pull Request that changes files that they are marked as owners of.

1. Go to [.github\CODEOWNERS](../../.github/CODEOWNERS)
2. Following the [CODEOWNERS documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners), add yourself as owner to files that you wish to be automatically requested as reviewer for.
   
   For example, if you wish to add yourself as a default reviewer for all pull requests, add your GitHub username to the same line as the `*` designator:  

   ```diff
   - * @abroddrick
   + * @abroddrick @YourGitHubUser
   ```

3. Create a pull request to finalize your changes

## Viewing Logs

If you run via `docker-compose up`, you'll see the logs in your terminal.

If you run via `docker-compose up -d`, you can get logs with `docker-compose logs -f`.

You can change the logging verbosity, if needed. Do a web search for "django log level".

## Mock data

There is a `post_migrate` signal in [signals.py](../../src/registrar/signals.py) that will load the fixtures from [fixtures_user.py](../../src/registrar/fixtures_users.py) and [fixtures_applications.py](../../src/registrar/fixtures_applications.py), giving you some test data to play with while developing.

See the [database-access README](./database-access.md) for information on how to pull data to update these fixtures.

## Running tests

Crash course on Docker's `run` vs `exec`: in order to run the tests inside of a container, a container must be running. If you already have a container running, you can use `exec`. If you do not, you can use `run`, which will attempt to start one.

To get a container running:

```shell
cd src
docker-compose build
docker-compose up -d
```

Django's test suite:

```shell
docker-compose exec app ./manage.py test
```

OR

```shell
docker-compose exec app python -Wa ./manage.py test  # view deprecation warnings
```

Linters:

```shell
docker-compose exec app ./manage.py lint
```

### Testing behind logged in pages

To test behind logged in pages with external tools, like `pa11y-ci` or `OWASP Zap`, add

```
"registrar.tests.common.MockUserLogin"
```

to MIDDLEWARE in settings.py. **Remove it when you are finished testing.**

### Reducing console noise in tests

Some tests, particularly when using Django's test client, will print errors.

These errors do not indicate test failure, but can make the output hard to read.

To silence them, we have a helper function `less_console_noise`:

```python
from .common import less_console_noise
...
        with less_console_noise():
            # <test code goes here>
```

### Accessibility Testing in the browser

We use the [ANDI](https://www.ssa.gov/accessibility/andi/help/install.html) browser extension 
from ssa.gov for accessibility testing outside the pipeline. 

ANDI will get blocked by our CSP settings, so you will need to install the 
[Disable Content-Security-Policy extension](https://chrome.google.com/webstore/detail/disable-content-security/ieelmcmcagommplceebfedjlakkhpden) 
and activate it for the page you'd like to test.

Note - refresh after enabling the extension on a page but before clicking ANDI.

### Accessibility Scanning

The tool `pa11y-ci` is used to scan pages for compliance with a set of
accessibility rules. The scan runs as part of our CI setup (see
`.github/workflows/test.yaml`) but it can also be run locally. To run locally,
type

```shell
docker-compose run pa11y npm run pa11y-ci
```

The URLs that `pa11y-ci` will scan are configured in `src/.pa11yci`. When new
views and pages are added, their URLs should also be added to that file.

### Security Scanning

The tool OWASP Zap is used for scanning the codebase for compliance with
security rules. The scan runs as part of our CI setup (see
`.github/workflows/test.yaml`) but it can also be run locally. To run locally,
type

```shell
docker-compose run owasp
```

# Images, stylesheets, and JavaScript

We use the U.S. Web Design System (USWDS) for styling our applications.

Static files (images, CSS stylesheets, JavaScripts, etc) are known as "assets".

Assets are stored in `registrar/assets` during development and served from `registrar/public`. During deployment, assets are copied from `registrar/assets` into `registrar/public`. Any assets which need processing, such as USWDS Sass files, are processed before copying.

**Note:** Custom images are added to `/registrar/assets/img/registrar`, keeping them separate from the images copied over by USWDS. However, because the `/img/` directory is listed in `.gitignore`, any files added to `/registrar/assets/img/registrar` will need to be force added (i.e. `git add --force <img-file>`) before they can be deployed. 

We utilize the [uswds-compile tool](https://designsystem.digital.gov/documentation/getting-started/developers/phase-two-compile/) from USWDS to compile and package USWDS assets.

## Making and viewing style changes

When you run `docker-compose up` the `node` service in the container will begin to watch for changes in the `registrar/assets` folder, and will recompile once any changes are made.

Within the `registrar/assets` folder, the `_theme` folder contains three files initially generated by `uswds-compile`:
1. `_uswds-theme-custom-styles` contains all the custom styles created for this application
2. `_uswds-theme` contains all the custom theme settings (e.g. primary colors, fonts, banner color, etc..)
3. `styles.css` a entry point or index for the styles, forwards all of the other style files used in the project (i.e. the USWDS source code, the settings, and all custom stylesheets).

You can also compile the **Sass** at any time using `npx gulp compile`. Similarly, you can copy over **other static assets** (images and javascript files), using `npx gulp copyAssets`.

## Upgrading USWDS and other JavaScript packages

Version numbers can be manually controlled in `package.json`. Edit that, if desired.

Now run `docker-compose run node npm update`.

Then run `docker-compose up` to recompile and recopy the assets.

Examine the results in the running application (remember to empty your cache!) and commit `package.json` and `package-lock.json` if all is well.

## Finite State Machines

In an effort to keep our domain logic centralized, we are representing the state of 
objects in the application using the [django-fsm](https://github.com/viewflow/django-fsm)
library. See the [ADR number 15](../architecture/decisions/0015-use-django-fs.md) for
more information on the topic.

## Login Time Bug

If you are seeing errors related to openid complaining about issuing a token from the future like this:

```
ERROR [djangooidc.oidc:243] Issued in the future
```

it may help to resync your laptop with time.nist.gov: 

```
sudo sntp -sS time.nist.gov
```

## Connection pool
To handle our connection to the registry, we utilize a connection pool to keep a socket open to increase responsiveness. In order to accomplish this, we are utilizing a heavily modified version of the (geventconnpool)[https://github.com/rasky/geventconnpool] library.

### Settings
The config for the connection pool exists inside the `settings.py` file.
| Name                     | Purpose                                                                                           |
| ------------------------ | ------------------------------------------------------------------------------------------------- |
| EPP_CONNECTION_POOL_SIZE | Determines the number of concurrent sockets that should exist in the pool.                        |
| POOL_KEEP_ALIVE          | Determines the interval in which we ping open connections in seconds. Calculated as POOL_KEEP_ALIVE / EPP_CONNECTION_POOL_SIZE |
| POOL_TIMEOUT             | Determines how long we try to keep a pool alive for, before restarting it.                        |

Consider updating the `POOL_TIMEOUT` or `POOL_KEEP_ALIVE` periods if the pool often restarts. If the pool only restarts after a period of inactivity, update `POOL_KEEP_ALIVE`. If it restarts during the EPP call itself, then `POOL_TIMEOUT` needs to be updated.

### Test if the connection pool is running
Our connection pool has a built-in `pool_status` object which you can call at anytime to assess the current connection status of the pool. Follow these steps to access it.

1. `cf ssh getgov-{env-name} -i {instance-index}`
* env-name -> Which environment to target, e.g. `staging`
* instance-index -> Which instance to target. For instance, `cf ssh getgov-staging -i 0`
2. `/tmp/lifecycle/shell`
3. `./manage.py shell`
4. `from epplibwrapper import CLIENT as registry, commands`
5. `print(registry.pool_status.connection_success)`
* Should return true

If you have multiple instances (staging for example), then repeat commands 1-5 for each instance you want to test. 