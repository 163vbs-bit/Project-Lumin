import { motion } from "framer-motion";
import type { PropsWithChildren } from "react";

export function AnimatedPage({ children }: PropsWithChildren) {
  return (
    <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.38, ease: "easeOut" }}>
      {children}
    </motion.div>
  );
}
