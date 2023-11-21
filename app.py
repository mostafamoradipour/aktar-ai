from aktarai import Orchestrator
import yaml


if __name__ == "__main__":
    user = "parand-sub"
    with open("config.yaml", 'r') as f:
        cfg = yaml.safe_load(f)
    cfg = cfg[user]
    orchestrator = Orchestrator(cfg)
    orchestrator.ft_run()
