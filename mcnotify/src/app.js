const defaults = require('./defaults');

module.exports = class App {
  constructor(context, config, logger) {
    this.context = context;
    this.config = Object.assign({}, defaults, config);
    this.logger = logger;
  }

  log(message, type = 'info') {
    if (!this.config.perform) {
      message += ' (dry run)';
    }
    this.logger[type](message);
  }

  getSubsByLabel(label) {
    return this.config.subscriptions.filter(
      sub => sub.events.labeled === label
    );
  }

  async labeled() {
    if (this.context.isBot || this.context.payload.issue.pull_request) {
      return;
    }

    const {perform} = this.config;

    const label = this.context.payload.label.name;
    const subs = this.getSubsByLabel(label);
    if (subs.length === 0) {
      return;
    }

    const {owner, repo, number} = this.context.issue();
    const issueData = this.context.payload.issue;

    for (const sub of subs) {
      if (!sub.issue || !sub.comment) {
        continue;
      }
      const target = {owner, repo, number: sub.issue};
      const targetUrl = `${owner}/${repo}/issues/${target.number}`;

      this.log(`[${targetUrl}] Unlocking`);
      if (perform) {
        try {
          await this.context.github.issues.unlock(target);
        } catch (e) {
          if (e.code === 404) {
            this.log(`[${targetUrl}] Issue does not exist`);
            continue;
          }
          throw e;
        }
      }

      const comment = sub.comment
        .replace(/{label}/, label)
        .replace(/{issue-author}/, issueData.user.login)
        .replace(/{issue-title}/, issueData.title)
        .replace(
          /{issue-url}/,
          `https://github.com/${owner}/${repo}/issues/${number}`
        );

      this.log(`[${targetUrl}] Commenting`);
      if (perform) {
        await this.context.github.issues.createComment({
          ...target,
          body: comment
        });
      }

      this.log(`[${targetUrl}] Locking`);
      if (perform) {
        await this.context.github.issues.lock(target);
      }
    }
  }
};
