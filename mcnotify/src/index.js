const App = require('./app');

module.exports = robot => {
  robot.on('issues.labeled', async context => {
    const app = await getApp(context);
    await app.labeled();
  });

  async function getApp(context) {
    let config = await context.config('mcnotify.yml');
    if (!config) {
      config = {perform: false};
    }

    return new App(context, config, robot.log);
  }
};
