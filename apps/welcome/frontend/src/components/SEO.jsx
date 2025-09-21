import { Helmet } from "react-helmet-async";
import { useLocation } from "react-router-dom";

const SEO = ({
  title = "Free Preventive Maintenance Plan Generator | ArcTecFox",
  description = "Generate a preventive maintenance plan in under 2 minutes with our free tool. CMMS-ready export to Excel/CSV. Built for asset-heavy teams.",
  noindex = false,
  image, // optional og:image
}) => {
  const location = useLocation();

  // In prod, set VITE_SITE_URL=https://arctecfox.ai
  const runtimeOrigin =
    (typeof window !== "undefined" && window.location && window.location.origin) ||
    "https://arctecfox.ai";
  const baseUrl = import.meta?.env?.VITE_SITE_URL || runtimeOrigin;

  const path = location?.pathname || "/";
  const canonicalUrl = `${baseUrl}${path}`;
  const fullTitle = title.includes("ArcTecFox") ? title : `${title} | ArcTecFox`;

  return (
    <Helmet>
      <title>{fullTitle}</title>
      <meta name="description" content={description} />
      <link rel="canonical" href={canonicalUrl} />

      <meta name="robots" content={noindex ? "noindex,nofollow" : "index,follow"} />

      {/* Open Graph */}
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:url" content={canonicalUrl} />
      <meta property="og:type" content="website" />
      {image ? <meta property="og:image" content={image} /> : null}

      {/* Twitter */}
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:card" content="summary_large_image" />
      {image ? <meta name="twitter:image" content={image} /> : null}
    </Helmet>
  );
};

export default SEO;
