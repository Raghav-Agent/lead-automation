import { useState } from "react";
import { motion } from "framer-motion";
import { Send } from "lucide-react";
import { toast } from "sonner";

const services = [
  "General Dentistry",
  "Teeth Whitening",
  "Dental Implants",
  "Orthodontics",
  "Root Canal Treatment",
  "Pediatric Dentistry",
];

const AppointmentForm = () => {
  const [form, setForm] = useState({
    name: "",
    phone: "",
    email: "",
    service: "",
    date: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    toast.success("Appointment request sent! We'll contact you shortly.");
    setForm({ name: "", phone: "", email: "", service: "", date: "" });
  };

  const inputClass =
    "w-full px-4 py-3 rounded-lg border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-colors text-sm";

  return (
    <section id="appointment" className="section-padding section-alt">
      <div className="max-w-7xl mx-auto">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.5 }}
          >
            <span className="text-primary font-semibold text-sm uppercase tracking-wider">Appointment</span>
            <h2 className="text-3xl md:text-4xl font-heading font-bold mt-2 mb-4 text-foreground">
              Book Your Visit Today
            </h2>
            <p className="text-muted-foreground leading-relaxed mb-6">
              Ready to take the first step toward a healthier smile? Fill out the form
              and our team will get back to you within 24 hours to confirm your appointment.
            </p>
            <div className="space-y-3 text-sm text-muted-foreground">
              <p>📞 We'll call to confirm your preferred time</p>
              <p>📧 You'll receive a confirmation email</p>
              <p>🕐 Same-day appointments available</p>
            </div>
          </motion.div>

          <motion.form
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.5 }}
            onSubmit={handleSubmit}
            className="bg-card rounded-2xl p-6 md:p-8 card-shadow space-y-4"
          >
            <input
              type="text"
              placeholder="Full Name"
              required
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className={inputClass}
            />
            <div className="grid sm:grid-cols-2 gap-4">
              <input
                type="tel"
                placeholder="Phone Number"
                required
                value={form.phone}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
                className={inputClass}
              />
              <input
                type="email"
                placeholder="Email Address"
                required
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                className={inputClass}
              />
            </div>
            <select
              required
              value={form.service}
              onChange={(e) => setForm({ ...form, service: e.target.value })}
              className={inputClass}
            >
              <option value="" disabled>Select a Service</option>
              {services.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
            <input
              type="date"
              required
              value={form.date}
              onChange={(e) => setForm({ ...form, date: e.target.value })}
              className={inputClass}
            />
            <button
              type="submit"
              className="w-full bg-primary text-primary-foreground py-3.5 rounded-lg font-semibold flex items-center justify-center gap-2 hover:opacity-90 transition-opacity"
            >
              <Send className="w-4 h-4" />
              Request Appointment
            </button>
          </motion.form>
        </div>
      </div>
    </section>
  );
};

export default AppointmentForm;
