# Chandar-lab Website

Jekyll setup and content for https://chandar-lab.github.io/

## Maintenance

If there are updates to people, publications, or news you can in most cases easily update this information yourself.
If you need help you can contact the current maintainer. If you don't speak French and need to provide French information,
just create a PR with the English content and contact the French maintainer to help you.

**Guides:**

* [Publications](#publications)
* [Theses](#theses)
* [News](#news)
* [Join Us](#join-us)
* [About the Lab](#about-the-lab)
* [People](#people)
  * [When someone joins the group](#when-someone-joins-the-group)
  * [When someone graduates but stays](#when-someone-graduates-but-stays-for-example-from-master-to-phd)
  * [When someone leaves the group](#when-someone-leaves-the-group)

### Publications

When a publication is added or changed:

1. Update [`_data/publications.yaml`](https://github.com/chandar-lab/chandar-lab.github.io/edit/master/_data/publications.yaml)
2. Create a pull request and ask the current maintainer to review.

### Theses

When a thesis is added or changed:

1. Update [`_data/theses.yaml`](https://github.com/chandar-lab/chandar-lab.github.io/edit/master/_data/theses.yaml)
2. Create a pull request and ask the current maintainer to review.

_If the thesis is not already a public document through the university, add it to [our Google Drive](https://drive.google.com/drive/folders/1g8dLImUtkY3PpmgXexx_HM3rNOZk1NYr)._

### News

When the news section needs to be changed:

1. Update [`_data/news.yaml`](https://github.com/chandar-lab/chandar-lab.github.io/edit/master/_data/news.yaml)
2. Create a pull request and ask the current maintainer to review.

_Note, old news are not deleted but hidden by setting a `hidden: true` property._

### Join Us

When the _Join Us_ section needs to be changed:

1. Update [`_i18n/en/join.md`](https://github.com/chandar-lab/chandar-lab.github.io/edit/master/_i18n/en/join.md)
2. Update [`_i18n/fr/join.md`](_i18n/fr/join.md) in the same branch.
3. Create a pull request.

### About the Lab

When the _About the Lab_ section needs to be changed:

1. Update [`_i18n/en/about.md`](https://github.com/chandar-lab/chandar-lab.github.io/edit/master/_i18n/en/about.md)
2. Update [`_i18n/fr/about.md`](_i18n/fr/about.md) in the same branch.
3. Create a pull request.

### People

_Note: Only the maintainer is expected to do this._

#### When someone joins the group:

1. Add them to [`_data/people.yaml`](https://github.com/chandar-lab/chandar-lab.github.io/edit/master/_data/people.yaml)
2. Add their profile picture too [`assets/images/bios/`](assets/images/bios/).
3. Use the `compress_bios.sh` or smiliar, to compress their profile picture to an appropriate size.
2. Create a pull request.

_To aid the process, you can send them this:_

> To add you to the website, I will need this information.
> * Your name
> * Are you a PhD student, a master student, or an intern?
> * Your profile picture in square format. This is optional, if you don't want your face on the website.
> * Your website (this is mandatory)
> * Your co-supervisor, if any.
> * Your start date
> * Your topic of interests. See https://chandar-lab.github.io/people/ for examples. If you know French, then please provide translations too.

#### When someone graduates but stays. For example, from Master to PhD:

1. Add their current profile (e.g. master) to [`_data/alumni.yaml`](https://github.com/chandar-lab/chandar-lab.github.io/edit/master/_data/alumni.yaml).
2. Update their current profile in [`_data/people.yaml`](_data/people.yaml) to the new title (e.g PhD) and start date in the same branch.
3. Create a pull request.

#### When someone leaves the group:

1. Remove them from [`_data/people.yaml`](https://github.com/chandar-lab/chandar-lab.github.io/edit/master/_data/people.yaml)
2. Remove their profile picture from [`assets/images/`](assets/images/).
2. Add them to [`_data/alumni.yaml`](_data/alumni.yaml) in the same branch.
3. Create a pull request.

## Local development

As the maintainer you may need to make modification which require local validation:

### Install

```bash
bundle install
```

### Build

```bash
LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 bundle exec jekyll serve
```
