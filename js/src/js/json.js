import { Transport } from "./transports";
import { Update } from "./update";

export class JSONTransport extends Transport {
  constructor() {
    super();
    this.onInitial.bind(this);
    this._update_to_model.bind(this);
    this.send.bind(this);
    this.receive.bind(this);
  }

  // ##################
  // # Client methods #
  // ##################
  async onInitial(update) {
    const update_inst = await this._update_to_model(update);
    return super.onInitial(update_inst);
  }

  async _update_to_model(update) {
    // first, parse out the json into a dict
    const data = JSON.parse(update);

    // now lookup the model map
    if (Object.keys(data).indexOf("model_type") < 0) {
      throw new Error(`Update data has no 'model_type'`);
    }

    if (Object.keys(data).indexOf("model_target") < 0) {
      throw new Error(`Update data has no 'model_target'`);
    }

    if (!this.model_map.has(data.model_type)) {
      throw new Error(
        `Class type (${data.model_type}) not known, did you forget to call 'hosts'?"`,
      );
    }

    // grab the class type
    const Class_type = this.model_map.get(data.model_type);

    // instantiate the inital model
    const model_inst = new Class_type(data.model);
    data.model = model_inst;

    //  defer to parent now that we have the model
    return new Update(data);
  }

  // #################
  // # Bidirectional #
  // #################
  async send(client_id) {
    return (await super.send(client_id)).json();
  }

  async receive(client_id, update) {
    const update_inst = await this._update_to_model(update);
    await super.receive(client_id, update_inst);
  }
}
