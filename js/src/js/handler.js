/* eslint-disable */
import {Client} from "./client";

export class WebSocketClient extends Client {
  constructor(options = {}) {
    super();
    this._transport = options.transport;
    this._model = options.model;
    this._config = options.config;

    // websocket connection information
    this._protocol =
      options.protocol || window.location.protocol === "http:" ? "ws:" : "wss:";
    this._host = options.host || window.location.host;
    this._path = options.path || "ws";
    this._connected = false;

    // data queue
    this._data = new Array();
    this._datapromise = null;
    this._datacallback = null;

    // binding
    this.connect.bind(this);
    this.disconnect.bind(this);
    this.receive.bind(this);
    this.send.bind(this);
  }

  async connect() {
    this._websocket = new WebSocket(
      `${this._protocol}//${this._host}/${this._path}`,
    );
    this._connected = true;
    this._websocket.onopen = this._on_open.bind(this);
    this._websocket.onclose = this._on_close.bind(this);
    this._websocket.onmessage = this._on_receive.bind(this);
  }

  async disconnect() {
    this._websocket.close();
  }
  
  async _on_open() {
    this._connected = true;
  }
  
  async _on_close(event) {
    this._connected = false;
    if (this._datacallback) {
      this._datacallback.reject(event);
      this._datacallback = null;
    }
  }

  async _on_receive(event) {
    // push data into queue
    this._data.push(event.data);

    // resolve if needed
    if (this._datacallback) {
      this._datacallback.resolve(this._data.shift());
      this._datacallback = null;
    }
  }

  async receive() {
    if (this._data.length !== 0) {
      // resolve immediately
      return Promise.resolve(this._data.shift());
    }

    // if disconnected, reject
    if (!this._connected) {
      return Promise.reject(new Error("Disconnected"));
    }

    // if already waiting to receive, return the same
    if (this._datacallback) {
      return this._datapromise;
    }

    // else, setup receiver
    this._datapromise = new Promise((resolve, reject) => {
      this._datacallback = {resolve, reject};
    });
    return this._datapromise;
  }

  async send(update) {
    this._websocket.send(update);
  }
}
