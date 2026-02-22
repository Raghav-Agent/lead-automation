import { motion } from "framer-motion";
import { Stethoscope, Sparkles, CircleDot, SmilePlus, HeartPulse, Baby } from "lucide-react";
import { type ReactNode } from "react";

interface ServiceCard {
  icon: ReactNode;
  title: string;
  description: string;
}

const services: ServiceCard[] = [
  {
    icon: <Stethoscope className="w-6 h-6" />,
    title: "General Dentistry",
    description: "Comprehensive check-ups, cleanings, and preventive care to maintain your oral health.",
  },
  {
    icon: <Sparkles className="w-6 h-6" />,
    title: "Teeth Whitening",
    description: "Professional whitening treatments for a brighter, more confident smile.",
  },
  {
    icon: <CircleDot className="w-6 h-6" />,
    title: "Dental Implants",
    description: "Permanent, natural-looking tooth replacements for a complete smile.",
  },
  {
    icon: <SmilePlus className="w-6 h-6" />,
    title: "Orthodontics",
    description: "Modern braces and clear aligners for perfectly straight teeth.",
  },
  {
    icon: <HeartPulse className="w-6 h-6" />,
    title: "Root Canal Treatment",
    description: "Gentle, pain-free root canal therapy to save damaged teeth.",
  },
  {
    icon: <Baby className="w-6 h-6" />,
    title: "Pediatric Dentistry",
    description: "Fun, friendly dental care designed specifically for children.",
  },
];

const containerVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.1 },
  },
};

const cardVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

const Services = () => {
  return (
    <section id="services" className="section-padding section-alt">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <span className="text-primary font-semibold text-sm uppercase tracking-wider">What We Offer</span>
          <h2 className="text-3xl md:text-4xl font-heading font-bold mt-2 mb-4 text-foreground">
            Our Services
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            From routine check-ups to advanced procedures, we provide a full range of dental services
            using the latest technology.
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {services.map((service) => (
            <motion.div
              key={service.title}
              variants={cardVariants}
              className="bg-card rounded-xl p-6 card-shadow hover:card-shadow-hover transition-shadow duration-300 group"
            >
              <div className="w-12 h-12 rounded-lg bg-primary/10 text-primary flex items-center justify-center mb-4 group-hover:bg-primary group-hover:text-primary-foreground transition-colors duration-300">
                {service.icon}
              </div>
              <h3 className="font-heading font-semibold text-lg mb-2 text-foreground">
                {service.title}
              </h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                {service.description}
              </p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default Services;
