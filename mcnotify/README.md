# McNotify

McNotify is a GitHub App built with [Probot](https://github.com/probot/probot)
that comments on predefined issues after certain events.
At Kivy it is used for notifying interested users
about [breaking changes](https://github.com/kivy/kivy/issues/5560).

## Usage

1. Create a GitHub App and deploy it
3. Open and lock an issue which will act as a notification thread, ask users to subscribe to it
2. Create and customize `.github/mcnotify.yml` based on the following template
4. Start labeling issues

Create `.github/mcnotify.yml` in the default branch to enable the app.
The file can be empty, or it can override any of these default settings:

```yml
# Configuration for McNotify - https://github.com/kivy/mcnotify

subscriptions:
  - events:
      # Events which trigger notifications
      labeled: mclabel
    # Issue used for posting notifications
    issue: 1
    # Comment to post on the notification thread. Optional placeholders: {label},
    # {issue-author}, {issue-title} and {issue-url}
    comment: >
      This is a notification for [{issue-title}]({issue-url}),
      opened by @{issue-author}.
```

## Deployment

See [docs/deploy.md](docs/deploy.md) if you would like to run your own
instance of this app.

## License

McNotify is released under the terms of the MIT License.
Please refer to the LICENSE file.
