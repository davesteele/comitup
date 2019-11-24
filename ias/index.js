const puppeteer = require("puppeteer-core");
const { spawn } = require("child_process");

const args = require("args-parser")(process.argv);
const ias_script = require(args.puppeteer_script_filepath);

(async () => {
  const { browser, close_browser } = await (async () => {
    try {
      // workaround to get puppeteer working with the version of chromium shipped with Raspberry Pi's
      const DISPLAY = ":1",
        WIDTH = 640,
        HEIGHT = 480;

      const xvfb_cmd = `Xvfb ${DISPLAY} -screen 0 ${WIDTH}x${HEIGHT}x24`;
      console.log(`Starting Xvfb with ${xvfb_cmd}`);
      const [exe, ...args] = xvfb_cmd.split(" ");
      const xvfb_process = spawn(exe, args);

      console.log("Opening browser");
      const browser = await puppeteer.launch({
        defaultViewport: { height: HEIGHT, width: WIDTH },
        headless: false, // use non-headless mode with xvfb called beforehand to circumvent raspi-specific bug
        executablePath: "chromium-browser",
        args: [`--display=${DISPLAY}`, "--no-sandbox", "--disable-extensions"]
      });
      return {
        browser,
        close_browser: async () => {
          await browser.close();
          xvfb_process.kill();
        }
      };
    } catch (e) {
      console.log(`Chromium failed with error: ${e}\n, trying google-chrome`);
      // give google chrome a shot instead. If just debian, this may not work at all.
      // Need to consult Dave @ dteele@debian.com on how to best handle this
      return {
        browser: await puppeteer.launch({ executablePath: "google-chrome" }),
        close_browser: browser.close
      };
    }
  })();

  await ias_script(browser, args);

  await close_browser();

  console.log("login script complete! WAN should now be accessible.");
})();
