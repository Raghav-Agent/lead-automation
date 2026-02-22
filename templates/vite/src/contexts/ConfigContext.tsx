import { createContext, useContext, useState, useEffect, ReactNode } from "react";

type Config = {
  business_name: string;
  niche: string;
  lead_id?: number;
};

const ConfigContext = createContext<Config | null>(null);

export const ConfigProvider = ({ children }: { children: ReactNode }) => {
  const [config, setConfig] = useState<Config | null>(null);
  useEffect(() => {
    fetch("/config.json")
      .then((r) => r.json())
      .then(setConfig)
      .catch(() => setConfig({ business_name: "", niche: "" }));
  }, []);
  return <ConfigContext.Provider value={config}>{children}</ConfigContext.Provider>;
};

export const useConfig = () => useContext(ConfigContext);
