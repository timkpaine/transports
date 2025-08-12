/* eslint-disable */

export class Transport {
  constructor() {
    this.models = new Map();
    this.server_models = new Map();
    this.model_map = new Map();

    this.hosts.bind(this);
  }

  hosts(model_type) {
    if (!this.model_map.has(model_type.name)) {
      console.info(`Registering type: ${model_type.name}`);
      this.model_map.set(model_type.name, model_type);

      // register any other models we find
      model_type.submodels().forEach((submodel_type) => {
        this.hosts(submodel_type);
      });
    }
  }

  async connect() {}

  async disconnect() {
    this.server_models = new Map();
  }

  async onInitial(update) {
    // TODO multi model and events
    const model = update.model;

    // register in model map
    this.server_models.set(model.id, model);

    // FIXME
    this.models.set("", model);

    // return the instance
    return model;
  }

  // #################
  // # Bidirectional #
  // #################
  async send(client_id) {
    // grab model from client
    const model = this.models.get(client_id);

    // pull latest send update
    return await model.get(); // TODO unneeded await but better stack trace
  }

  async receive(client_id, update) {
    // grab model from client
    const model = this.models.get(client_id);

    // push update to model
    await model.receive(update);
  }
}
