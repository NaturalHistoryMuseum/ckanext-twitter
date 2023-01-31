<!--header-start-->
<img src="https://github.com/NaturalHistoryMuseum/ckanext-twitter/raw/main/.github/nhm-logo.svg" align="left" width="150px" height="100px" hspace="40"/>

# ckanext-twitter

[![Tests](https://img.shields.io/github/actions/workflow/status/NaturalHistoryMuseum/ckanext-twitter/main.yml?style=flat-square)](https://github.com/NaturalHistoryMuseum/ckanext-twitter/actions/workflows/main.yml)
[![Coveralls](https://img.shields.io/coveralls/github/NaturalHistoryMuseum/ckanext-twitter/main?style=flat-square)](https://coveralls.io/github/NaturalHistoryMuseum/ckanext-twitter)
[![CKAN](https://img.shields.io/badge/ckan-2.9.7-orange.svg?style=flat-square)](https://github.com/ckan/ckan)
[![Python](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue.svg?style=flat-square)](https://www.python.org/)
[![Docs](https://img.shields.io/readthedocs/ckanext-twitter?style=flat-square)](https://ckanext-twitter.readthedocs.io)

_A CKAN extension that enables users to post a tweet every time a dataset is created or updated._

<!--header-end-->

# Overview

<!--overview-start-->
This extension connects a CKAN instance to a Twitter account so that when a dataset is updated or created (i.e. the `after_update` hook is called), the user has the option to post a tweet about the activity.

<!--overview-end-->

# Installation

<!--installation-start-->
Path variables used below:
- `$INSTALL_FOLDER` (i.e. where CKAN is installed), e.g. `/usr/lib/ckan/default`
- `$CONFIG_FILE`, e.g. `/etc/ckan/default/development.ini`

## Installing from PyPI

```shell
pip install ckanext-twitter
```

## Installing from source

1. Clone the repository into the `src` folder:
   ```shell
   cd $INSTALL_FOLDER/src
   git clone https://github.com/NaturalHistoryMuseum/ckanext-twitter.git
   ```

2. Activate the virtual env:
   ```shell
   . $INSTALL_FOLDER/bin/activate
   ```

3. Install via pip:
   ```shell
   pip install $INSTALL_FOLDER/src/ckanext-twitter
   ```

### Installing in editable mode

Installing from a `pyproject.toml` in editable mode (i.e. `pip install -e`) requires `setuptools>=64`; however, CKAN 2.9 requires `setuptools==44.1.0`. See [our CKAN fork](https://github.com/NaturalHistoryMuseum/ckan) for a version of v2.9 that uses an updated setuptools if this functionality is something you need.

## Post-install setup

1. Add 'twitter' to the list of plugins in your `$CONFIG_FILE`:
   ```ini
   ckan.plugins = ... twitter
   ```

2. Add a 'tweet' block to `read_base.html`:
   ```jinja2
   {% block tweet %}
   {{ super() }}
   {% endblock %}
   ```

3. Optionally, override the styling of the block by creating an `ajax_snippets/edit_tweet.html` file.

<!--installation-end-->

# Configuration

<!--configuration-start-->
These are the options that can be specified in your .ini config file. The only _required_ options are the twitter credentials. Everything else has a sensible default set.

## **[REQUIRED]**

| Name                              | Description                  | Options |
|-----------------------------------|------------------------------|---------|
| `ckanext.twitter.consumer_key`    | Your Twitter consumer key    |         |
| `ckanext.twitter.consumer_secret` | Your Twitter consumer secret |         |
| `ckanext.twitter.token_key`       | Your Twitter token key       |         |
| `ckanext.twitter.token_secret`    | Your Twitter token secret    |         |

All of these can be obtained by creating a single-user app at [apps.twitter.com](https://apps.twitter.com). They can be found on the "keys and access tokens" tab when viewing your app.

## Tweet Templates

Tweets are generated using [Jinja2](http://jinja.pocoo.org) and use tokens derived from the package dictionary. See [Usage](#usage) for more detail.

| Name                      | Description                                | Default                                                                                                                                               |
|---------------------------|--------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| `ckanext.twitter.new`     | Template for tweets about new datasets     | `New dataset: "{{ title }}" by {{ author }} ({%- if records != 0 -%} {{ records }} records {%- else -%} {{ resources }} resource {%- endif -%}).`     |
| `ckanext.twitter.updated` | Template for tweets about updated datasets | `Updated dataset: "{{ title }}" by {{ author }} ({%- if records != 0 -%} {{ records }} records {%- else -%} {{ resources }} resource {%- endif -%}).` |

If your config is created dynamically using Jinja2, you will have to wrap any custom template in `{% raw %}{% endraw %}` tags and **add a newline after it**, e.g.:
```ini
ckanext.twitter.new = {% raw %}{{ title }} by {{ author }} ({{ records }} records) has just been published!{% endraw %}

ckanext.twitter.consumer_key = {{ twitter.consumer_key }}
ckanext.twitter...
```

## Other options

| Name                                   | Description                                                                                                                             | Options     | Default |
|----------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|-------------|---------|
| `ckanext.twitter.debug`                | Is in debug mode; overrides global debug flag if specified                                                                              | True, False | False   |
| `ckanext.twitter.hours_between_tweets` | Number of hours between tweets about the _same dataset_ (to prevent spamming)                                                           |             | 24      |
| `ckanext.twitter.disable_edit`         | If true, users will not be able to edit the tweet about their dataset before it is posted (though they can still decide not to post it) | True, False | False   |

<!--configuration-end-->

# Usage

<!--usage-start-->
## Tweet Templates

Token values for the tweet templates will come from a simplified package dictionary. In these, any collection values (i.e. lists and dictionaries) have been replaced with the number of items, the author list has been significantly shortened, and any long strings will be shortened to fit into the tweet character limit (currently set at 140).

For example, if the package dictionary is:
```python
{
  'author': 'Dippy Diplodocus, Sophie Stegosaurus',
  'author_email': None,
  'dataset_category': ['Citizen Science'],
  'doi': 'DOI_VALUE',
  'license_title': 'Creative Commons Attribution',
  'organization': {'description': '', 'name': 'nhm', 'is_organization': True, 'state': 'active'},
  'resources': [
                  {'mimetype': 'image/jpeg', 'name': 'resource_1.jpg', 'format': 'JPEG'},
                  {'mimetype': 'image/jpeg', 'name': 'resource_2.jpg', 'format': 'JPEG'}
               ],
  'title': 'Dataset Name'
}
```

Then the tokenised dictionary would be:

```python
{
  'author': 'Diplodocus et al.',  # just the surname of the first author
  # author_email was None so it's excluded
  'dataset_category': 1,  # lists are counted
  'doi': 'DOI_VALUE',  # simple string values stay the same
  'license_title': 'Creative Commons Attribution',
  'organization': 4,  # dicts are also counted
  'resources': 2,
  'title': 'Dataset Name'
}
```

And if you had defined the tweet template as:
```html+jinja
New dataset: "{{ title }}" by {{ author }} ({{ resources }} resources).
```

Your tweet would then read:

> New dataset: "Dataset Name" by Diplodocus et al. (2 resources)

<!--usage-end-->

# Testing

<!--testing-start-->
There is a Docker compose configuration available in this repository to make it easier to run tests. The ckan image uses the Dockerfile in the `docker/` folder.

To run the tests against ckan 2.9.x on Python3:

1. Build the required images:
   ```shell
   docker-compose build
   ```

2. Then run the tests.
   The root of the repository is mounted into the ckan container as a volume by the Docker compose
   configuration, so you should only need to rebuild the ckan image if you change the extension's
   dependencies.
   ```shell
   docker-compose run ckan
   ```

Note that the tests shouldn't make any calls to Twitter's API and won't post any tweets.

<!--testing-end-->
