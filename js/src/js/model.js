export class Model {
  constructor() {
    this.receive.bind(this);
  }

  static submodels() {
    // TODO ugly
    return [];
  }

  // eslint-disable-next-line class-methods-use-this, no-unused-vars
  receive(_data) {
    // To be implemented
  }
}
