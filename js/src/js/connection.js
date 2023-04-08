/* eslint-disable no-constant-condition */
/* eslint-disable class-methods-use-this */
/* eslint-disable no-await-in-loop */

export class Connection {
  constructor() {
    if (this.constructor === Connection) {
      throw new Error("Abstract classes can't be instantiated.");
    }

    this.receiver.bind(this);
    this.sender.bind(this);
  }

  async receiver() {
    while (true) {
      // grab from client
      const update = await this.receive();

      // send to transport to be sent to models
      await this._transport.receive(this._client_id, update);
    }
  }

  async sender() {
    while (true) {
      // get update from transport derived from models
      const update = await this._transport.send(this._client_id);
      // send to client
      await this.send(update);
    }
  }

  // eslint-disable-next-line no-unused-vars
  async connect(client_id = "") {
    throw new Error("Method 'connect' must be implemented.");
  }

  async disconnect() {
    throw new Error("Method 'disconnect' must be implemented.");
  }

  async receive() {
    throw new Error("Method 'receive' must be implemented.");
  }

  // eslint-disable-next-line no-unused-vars
  async send(update) {
    throw new Error("Method 'send' must be implemented.");
  }
}
