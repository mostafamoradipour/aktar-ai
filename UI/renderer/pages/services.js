import Card from "@/components/card";
export default function Services() {
  const items = [
    {
      href: "/services/smart-store",
      icon: "workspaces",
      description: "Vector Space",
    },
    {
      href: "/data-analytics",
      icon: "stacked_bar_chart",
      description: "Data Analytics",
    },
    {
      href: "",
      icon: "widgets",
      description: "Download App",
    },
    {
      href: "/contact-human",
      icon: "support_agent",
      description: "Contact Human",
    },
  ];
  return (
    <>
      <main className="grid">
        {items.map((item, i) => (
          <Card
            key={i}
            title={item.description}
            icon={item.icon}
            href={item.href}
          />
        ))}
      </main>
    </>
  );
}
