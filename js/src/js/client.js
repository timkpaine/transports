import { Connection } from "./connection";

export class Client extends Connection {
  constructor(options = {}) {
    super();
    this._transport = options.transport;
    this._client_id = options._client_id || "";

    this.open.bind(this);
    this.close.bind(this);
    this.initial.bind(this);
    this.handle.bind(this);
  }

  async open() {
    // wait for client connection
    await this.connect(this._client_id);

    // Notify transport of connection
    await this._transport.connect();

    // receive initial
    const initial = await this.receive();

    // register and return
    return this._transport.onInitial(initial);
  }

  async close() {
    // # Notify transport of connection
    await this._transport.disconnect();
    await this.disconnect();
  }

  async initial() {
    // run the open routing
    return this.open();
  }

  async handle() {
    // await Promise.any([this.sender(), this.receiver()]);
    await this.receiver();
    await this.close();
  }
}
