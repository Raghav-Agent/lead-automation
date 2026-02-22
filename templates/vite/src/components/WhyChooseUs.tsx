import { motion } from "framer-motion";
import { ShieldCheck, Clock, BadgeCheck, DollarSign } from "lucide-react";

const features = [
  {
    icon: <ShieldCheck className="w-7 h-7" />,
    title: "Painless Procedures",
    description: "Advanced techniques and sedation options for a comfortable, anxiety-free experience.",
  },
  {
    icon: <Clock className="w-7 h-7" />,
    title: "Flexible Appointments",
    description: "Evening and weekend slots available to fit your busy schedule.",
  },
  {
    icon: <BadgeCheck className="w-7 h-7" />,
    title: "Certified Specialists",
    description: "Our team holds advanced certifications in multiple dental specialties.",
  },
  {
    icon: <DollarSign className="w-7 h-7" />,
    title: "Affordable Pricing",
    description: "Transparent pricing with flexible payment plans and insurance support.",
  },
];

const WhyChooseUs = () => {
  return (
    <section id="why-us" className="section-padding section-alt">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <span className="text-primary font-semibold text-sm uppercase tracking-wider">Why Us</span>
          <h2 className="text-3xl md:text-4xl font-heading font-bold mt-2 mb-4 text-foreground">
            Why Choose Bright Smile?
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            We go above and beyond to make your dental experience exceptional.
          </p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className="text-center p-6"
            >
              <div className="w-16 h-16 rounded-2xl bg-primary/10 text-primary flex items-center justify-center mx-auto mb-5">
                {feature.icon}
              </div>
              <h3 className="font-heading font-semibold text-lg mb-2 text-foreground">
                {feature.title}
              </h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default WhyChooseUs;
