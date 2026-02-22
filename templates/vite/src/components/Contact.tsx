import { motion } from "framer-motion";
import { MapPin, Phone, Mail, Clock } from "lucide-react";
import { useConfig } from "@/contexts/ConfigContext";

const Contact = () => {
  const config = useConfig();
  const phone = config?.phone;
  const email = config?.business_name ? `contact@${config.business_name.toLowerCase().replace(/\s+/g, '')}.com` : "hello@brightsmile.com";

  return (
    <section id="contact" className="section-padding">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <span className="text-primary font-semibold text-sm uppercase tracking-wider">Contact</span>
          <h2 className="text-3xl md:text-4xl font-heading font-bold mt-2 mb-4 text-foreground">
            Find Us
          </h2>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Info */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.5 }}
            className="space-y-6"
          >
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0">
                <MapPin className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-heading font-semibold text-foreground mb-1">Address</h3>
                <p className="text-muted-foreground text-sm">123 Dental Avenue, Suite 200<br />New York, NY 10001</p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0">
                <Phone className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-heading font-semibold text-foreground mb-1">Phone</h3>
                <p className="text-muted-foreground text-sm">
                  {phone ? (
                    <a href={`tel:${phone}`} className="hover:underline">{phone}</a>
                  ) : (
                    "(555) 123-4567"
                  )}
                </p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0">
                <Mail className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-heading font-semibold text-foreground mb-1">Email</h3>
                <p className="text-muted-foreground text-sm">{email}</p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0">
                <Clock className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-heading font-semibold text-foreground mb-1">Working Hours</h3>
                <p className="text-muted-foreground text-sm">
                  Mon – Fri: 8:00 AM – 6:00 PM<br />
                  Saturday: 9:00 AM – 3:00 PM<br />
                  Sunday: Closed
                </p>
              </div>
            </div>
          </motion.div>

          {/* Map placeholder */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.5 }}
            className="rounded-2xl overflow-hidden card-shadow bg-muted min-h-[320px]"
          >
            <iframe
              title="Clinic Location"
              src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3022.9663095343008!2d-73.99074012452078!3d40.74076987138413!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x89c259a3f71c5cf1%3A0x524ed6a3e5fa8892!2sFlatiron%20Building!5e0!3m2!1sen!2sus!4v1700000000000!5m2!1sen!2sus"
              width="100%"
              height="100%"
              style={{ border: 0, minHeight: 320 }}
              allowFullScreen
              loading="lazy"
              referrerPolicy="no-referrer-when-downgrade"
            />
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default Contact;
