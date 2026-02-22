import { motion } from "framer-motion";
import heroImage from "@/assets/hero-dental.jpg";
import { useConfig } from "@/contexts/ConfigContext";

const Hero = () => {
  const config = useConfig();
  const businessName = config?.business_name || "Bright Smile Dental";

  return (
    <section className="relative min-h-[90vh] flex items-center overflow-hidden">
      {/* Background image */}
      <div className="absolute inset-0">
        <img
          src={heroImage}
          alt="Modern dental clinic with friendly dentist"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-foreground/80 via-foreground/50 to-transparent" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 md:px-8 w-full py-32">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: "easeOut" }}
          className="max-w-xl"
        >
          <span className="inline-block bg-accent/20 text-accent-foreground px-4 py-1.5 rounded-full text-sm font-medium mb-6 backdrop-blur-sm border border-accent/30">
            ✨ Welcome to {businessName}
          </span>
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-heading font-bold text-card-foreground leading-tight mb-6" style={{ color: 'hsl(0 0% 100%)' }}>
            Your Smile,{" "}
            <span className="text-accent">Our Priority</span>
          </h1>
          <p className="text-lg md:text-xl mb-8 leading-relaxed" style={{ color: 'hsl(0 0% 100% / 0.8)' }}>
            Experience gentle, modern dentistry in a comfortable environment. Our team
            is dedicated to giving you the healthy, beautiful smile you deserve.
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <a
              href="#appointment"
              className="bg-primary text-primary-foreground px-8 py-3.5 rounded-lg font-semibold text-center hover:opacity-90 transition-opacity shadow-lg"
            >
              Book an Appointment
            </a>
            <a
              href="#services"
              className="border border-card/30 backdrop-blur-sm px-8 py-3.5 rounded-lg font-semibold text-center hover:bg-card/10 transition-colors"
              style={{ color: 'hsl(0 0% 100%)' }}
            >
              Our Services
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default Hero;
