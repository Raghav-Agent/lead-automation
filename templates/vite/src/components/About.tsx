import { motion } from "framer-motion";
import { Award, Users, Cpu } from "lucide-react";
import dentistImage from "@/assets/dentist-portrait.jpg";

const stats = [
  { icon: <Award className="w-5 h-5" />, value: "15+", label: "Years Experience" },
  { icon: <Users className="w-5 h-5" />, value: "500+", label: "Happy Patients" },
  { icon: <Cpu className="w-5 h-5" />, value: "100%", label: "Modern Equipment" },
];

const About = () => {
  return (
    <section id="about" className="section-padding">
      <div className="max-w-7xl mx-auto">
        <div className="grid md:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Image */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
            className="relative"
          >
            <div className="rounded-2xl overflow-hidden card-shadow">
              <img
                src={dentistImage}
                alt="Dr. James Mitchell, Lead Dentist"
                className="w-full aspect-[4/5] object-cover"
              />
            </div>
            {/* Floating accent card */}
            <div className="absolute -bottom-4 -right-4 md:-right-6 bg-primary text-primary-foreground rounded-xl px-6 py-4 card-shadow">
              <p className="font-heading font-bold text-2xl">15+</p>
              <p className="text-sm opacity-90">Years of Excellence</p>
            </div>
          </motion.div>

          {/* Content */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
          >
            <span className="text-primary font-semibold text-sm uppercase tracking-wider">About Us</span>
            <h2 className="text-3xl md:text-4xl font-heading font-bold mt-2 mb-6 text-foreground">
              Trusted Dental Care for Your Entire Family
            </h2>
            <p className="text-muted-foreground leading-relaxed mb-6">
              At Bright Smile Dental, we believe everyone deserves a healthy, beautiful smile.
              Led by Dr. James Mitchell, our experienced team combines the latest dental
              technology with a warm, patient-centered approach to provide exceptional care
              in a comfortable environment.
            </p>
            <p className="text-muted-foreground leading-relaxed mb-8">
              Whether you need a routine cleaning or a complete smile makeover, we're here to
              help you achieve your dental goals with personalized treatment plans tailored to
              your needs.
            </p>

            <div className="grid grid-cols-3 gap-4">
              {stats.map((stat) => (
                <div
                  key={stat.label}
                  className="text-center p-4 rounded-xl bg-secondary/50"
                >
                  <div className="w-10 h-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center mx-auto mb-2">
                    {stat.icon}
                  </div>
                  <p className="font-heading font-bold text-xl text-foreground">{stat.value}</p>
                  <p className="text-muted-foreground text-xs mt-1">{stat.label}</p>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default About;
