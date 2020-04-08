var WorkOrderRegistry = artifacts.require("WorkOrderRegistry");
var WorkerRegistry = artifacts.require("WorkerRegistry");

module.exports = function(deployer) {
  deployer.deploy(WorkOrderRegistry);
  deployer.deploy(WorkerRegistry);
};
