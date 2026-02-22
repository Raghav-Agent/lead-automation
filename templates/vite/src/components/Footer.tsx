import { Facebook, Instagram, Twitter } from "lucide-react";
import { useConfig } from "@/contexts/ConfigContext";

const Footer = () => {
  const config = useConfig();
  const businessName = config?.business_name || "Bright Smile";

  return (
    <footer className="bg-foreground text-background">
      <div className="max-w-7xl mx-auto px-4 md:px-8 py-12">
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
                <span className="text-primary-foreground font-heading font-bold text-sm">BS</span>
              </div>
              <span className="font-heading font-bold text-lg">{businessName}</span>
            </div>
            <p className="text-sm opacity-70 leading-relaxed">
              Your trusted partner for a healthier, brighter smile. Quality dental care for the whole family.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="font-heading font-semibold mb-4">Quick Links</h4>
            <div className="space-y-2">
              {["Services", "About", "Testimonials", "Contact"].map((link) => (
                <a
                  key={link}
                  href={`#${link.toLowerCase()}`}
                  className="block text-sm opacity-70 hover:opacity-100 transition-opacity"
                >
                  {link}
                </a>
              ))}
            </div>
          </div>

          {/* Services */}
          <div>
            <h4 className="font-heading font-semibold mb-4">Services</h4>
            <div className="space-y-2">
              {["General Dentistry", "Teeth Whitening", "Dental Implants", "Orthodontics"].map((s) => (
                <p key={s} className="text-sm opacity-70">{s}</p>
              ))}
            </div>
          </div>

          {/* Social */}
          <div>
            <h4 className="font-heading font-semibold mb-4">Follow Us</h4>
            <div className="flex gap-3">
              {[Facebook, Instagram, Twitter].map((Icon, i) => (
                <a
                  key={i}
                  href="#"
                  className="w-10 h-10 rounded-lg bg-background/10 flex items-center justify-center hover:bg-primary transition-colors"
                >
                  <Icon className="w-4 h-4" />
                </a>
              ))}
            </div>
          </div>
        </div>

        <div className="border-t border-background/10 mt-10 pt-6 text-center">
          <p className="text-sm opacity-60">
            © {new Date().getFullYear()} {config?.business_name || "Bright Smile"}. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
