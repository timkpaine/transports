import { placeholder, foo} from "../src/js/transports";
import { initSync } from "../dist/pkg/transports";
import fs from "fs";


describe("Test", () => {
  beforeAll(async () => {
    const buffer = fs.readFileSync("./dist/pkg/transports_bg.wasm");
    initSync(buffer);
  });

  test("Test1", async () => {
    expect(placeholder).toBeDefined();
  });
  test("Test2", async () => {
    expect(foo()).toBeDefined();
  });
});
