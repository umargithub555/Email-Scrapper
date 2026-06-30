# from typing import List, Optional

# import os
# from dotenv import load_dotenv
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel, Field

# from google import genai
# from google.genai.types import (
#     GenerateContentConfig,
#     Tool,
#     GoogleSearch,
# )

# # -------------------------
# # Setup
# # -------------------------

# load_dotenv()

# client = genai.Client(
#     api_key=os.getenv("GEMINI_API_KEY")
# )

# app = FastAPI()


# # -------------------------
# # Request Model
# # -------------------------

# class DistributorRequest(BaseModel):
#     brand: str
#     country: str


# # -------------------------
# # Response Models
# # -------------------------

# class Distributor(BaseModel):
#     name: str = Field(description="Distributor company name")

#     website: Optional[str] = None

#     address: Optional[str] = None

#     city: Optional[str] = None

#     state: Optional[str] = None

#     country: Optional[str] = None

#     email: Optional[str] = None

#     phone: Optional[str] = None

#     contact_page: Optional[str] = None

#     official: bool

#     parent_company: Optional[str] = None

#     source: Optional[str] = None

#     confidence: int = Field(ge=0, le=100)


# class Output(BaseModel):
#     brand: str

#     country: str

#     manufacturer: Optional[str] = None

#     official_website: Optional[str] = None

#     manufacturer_contact_page: Optional[str] = None

#     manufacturer_email: Optional[str] = None

#     manufacturer_phone: Optional[str] = None

#     official_distributors: List[Distributor] = Field(default_factory=list)

#     notes: Optional[str] = None


# # -------------------------
# # Endpoint
# # -------------------------

# # @app.post("/find-distributors", response_model=Output)
# # async def extract_distributors(req: DistributorRequest):

# #     prompt = f"""
# #         You are an expert B2B market research analyst.

# #         Your task is to identify the official distributors for a given brand in a specific country.

# #         Brand:
# #         {req.brand}

# #         Country:
# #         {req.country}

# #         Instructions:

# #         1. Use Google Search to locate the manufacturer's official website.

# #         2. Determine the manufacturer's parent company if applicable.

# #         3. Search for:
# #         - Official distributors
# #         - Authorized distributors
# #         - Distributor locator pages
# #         - Where to buy pages
# #         - Dealer locator pages
# #         - Regional distributor pages

# #         4. Prefer information from:
# #         - The manufacturer's official website
# #         - Official regional websites
# #         - Official distributor directories

# #         5. If an official distributor is found, collect:
# #         - Company name
# #         - Website
# #         - Email
# #         - Phone number
# #         - Full address
# #         - Country
# #         - Parent company (if known)
# #         - Contact page
# #         - Source URL

# #         6. If multiple official distributors exist, include all of them.

# #         7. If no official distributors can be verified, do NOT invent any.
# #         Instead:
# #         - Set official_distributors_found to false.
# #         - Populate manufacturer contact information if available.
# #         - Set next_action to "contact_manufacturer".

# #         8. If distributor information comes from unofficial sources, mark:
# #         official = false
# #         and lower the confidence score.

# #         9. Confidence Guidelines:
# #         - 95–100: Listed directly on the manufacturer's official website.
# #         - 80–94: Listed on an official regional partner page.
# #         - 60–79: Found on a reputable distributor website but not confirmed by the manufacturer.
# #         - Below 60: Weak evidence.

# #         10. Never fabricate:
# #             - Email addresses
# #             - Phone numbers
# #             - Addresses
# #             - Websites
# #             - Parent companies

# #         If a value cannot be verified, return null.

# #         Always prioritize accuracy over completeness.

# #     """

# #     try:

# #         response = client.models.generate_content(
# #             model="gemini-2.5-flash",
# #             contents=prompt,
# #             config=GenerateContentConfig(
# #                 tools=[Tool(google_search=GoogleSearch())],
# #                 response_mime_type="application/json",
# #                 response_schema=Output,
# #                 temperature=0,
# #             ),
# #         )

# #         if response.parsed is None:
# #             raise HTTPException(
# #                 status_code=500,
# #                 detail="Gemini returned an invalid response."
# #             )

# #         return response.parsed

# #     except Exception as e:
# #         raise HTTPException(
# #             status_code=500,
# #             detail=str(e)
# #         )



# @app.post("/find-distributors", response_model=Output)
# async def extract_distributors(req: DistributorRequest):

#     research_prompt = f"""
#         You are an expert B2B market research analyst.

#         Your task is to identify the official distributors for a given brand in a specific country.

#         Brand: {req.brand}
#         Country: {req.country}

#         Instructions:

#         1. Use Google Search to locate the manufacturer's official website.
#         2. Determine the manufacturer's parent company if applicable.
#         3. Search for:
#            - Official distributors
#            - Authorized distributors
#            - Distributor locator pages
#            - Where to buy pages
#            - Dealer locator pages
#            - Regional distributor pages
#         4. Prefer information from:
#            - The manufacturer's official website
#            - Official regional websites
#            - Official distributor directories
#         5. If an official distributor is found, collect:
#            - Company name, website, email, phone, full address, country,
#              parent company (if known), contact page, source URL
#         6. If multiple official distributors exist, include all of them.
#         7. If no official distributors can be verified, do NOT invent any.
#            Instead say so explicitly and provide manufacturer contact info if available.
#         8. If distributor information comes from unofficial sources, say so explicitly
#            and note that confidence should be lower.
#         9. Confidence Guidelines:
#            - 95–100: Listed directly on the manufacturer's official website.
#            - 80–94: Listed on an official regional partner page.
#            - 60–79: Found on a reputable distributor website but not confirmed by manufacturer.
#            - Below 60: Weak evidence.
#         10. Never fabricate emails, phone numbers, addresses, websites, or parent companies.
#             If a value cannot be verified, say it is unknown.

#         Write out your findings in detail, citing where each piece of information came from.
#     """

#     try:
#         # Step 1: grounded research with Google Search (no JSON schema allowed here)
#         research_response = client.models.generate_content(
#             model="gemini-2.5-flash",
#             contents=research_prompt,
#             config=GenerateContentConfig(
#                 tools=[Tool(google_search=GoogleSearch())],
#                 temperature=0,
#             ),
#         )

#         research_text = research_response.text
#         if not research_text:
#             raise HTTPException(
#                 status_code=500,
#                 detail="Gemini returned no research content."
#             )

#         # Step 2: structure the research into the Output schema (no tools here)
#         structuring_prompt = f"""
#             Based on the research notes below, extract and structure the information
#             into the required schema.

#             Brand: {req.brand}
#             Country: {req.country}

#             Research notes:
#             {research_text}

#             Follow these rules:
#             - Never fabricate emails, phone numbers, addresses, websites, or parent companies.
#               If a value cannot be verified from the notes, return null.
#             - official_distributors should be an empty list if none were verified.
#             - Set official=false and lower confidence for distributors not confirmed by the
#               manufacturer directly.
#         """

#         structured_response = client.models.generate_content(
#             model="gemini-2.5-flash",
#             contents=structuring_prompt,
#             config=GenerateContentConfig(
#                 response_mime_type="application/json",
#                 response_schema=Output,
#                 temperature=0,
#             ),
#         )

#         if structured_response.parsed is None:
#             raise HTTPException(
#                 status_code=500,
#                 detail="Gemini returned an invalid structured response."
#             )

#         return structured_response.parsed

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=str(e)
#         )





from typing import List, Optional
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from google import genai
from google.genai.types import (
    GenerateContentConfig,
    Tool,
    GoogleSearch,
)

# -------------------------
# Setup
# -------------------------

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

app = FastAPI()


# -------------------------
# Request Model
# -------------------------

class DistributorRequest(BaseModel):
    brand: str
    country: str


# -------------------------
# Response Models
# -------------------------

class Distributor(BaseModel):
    name: str = Field(description="Distributor, commercial wholesaler, or regional supplier company name")
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    contact_page: Optional[str] = None
    official: bool = Field(description="True if verified as an authorized/commercial supplier, false if a secondary general wholesaler")
    source: Optional[str] = None
    confidence: int = Field(ge=0, le=100)


class Output(BaseModel):
    brand: str
    country: str
    parent_company: Optional[str] = None
    official_website: Optional[str] = None
    parent_company_email: Optional[str] = None
    parent_company_email_type: Optional[str] = Field(
        default=None,
        description="Type of contact this email reaches: 'investor_relations', 'media_press', 'corporate_general', or 'unknown'"
    )
    brand_contact_page: Optional[str] = None
    brand_emails: Optional[list] = []
    brand_phone: Optional[str] = None
    distributors: List[Distributor] = Field(default_factory=list, description="List of confirmed regional distributors, broad-line suppliers, or wholesalers")
    notes: Optional[str] = None




# Health Check

@app.get("/health")
def health_check():
    return {
        "status":200,
        "health": "OK ✅"
    }





# -------------------------
# Endpoint
# -------------------------

@app.post("/find-distributors", response_model=Output)
async def extract_distributors(req: DistributorRequest):

    research_prompt = f"""
            You are an expert B2B market research analyst conducting corporate due diligence.

            Brand: {req.brand}
            Country: {req.country}

            Your task has THREE priority objectives, in this order. Do not skip or shortcut objective 1 or 2 to save time on objective 3.

            OBJECTIVE 1 — PARENT COMPANY (mandatory dedicated search):
            - Search specifically for "{req.brand} parent company", "{req.brand} owned by", "{req.brand} corporate structure", and check the brand's official "About Us"/investor relations pages.
            - Identify the ultimate parent/holding company if the brand is a subsidiary. If the brand IS the parent (no parent exists), state that explicitly rather than leaving it ambiguous.
            - Identify the official corporate website of the brand itself.

            OBJECTIVE 1B — PARENT COMPANY CONTACT (mandatory dedicated search, only if a parent company exists):
            - If a parent company was identified in Objective 1, search specifically for "[parent company] investor relations contact", "[parent company] media contact", "[parent company] press contact", "[parent company] corporate contact email".
            - Parent companies rarely publish a general-purpose public email. What you will most often find is one of: an investor relations email, a media/press relations email, or a general corporate contact form/email. Capture whichever exists, and note explicitly which type it is — this matters more than finding just any email.
            - If the brand IS the parent company (no separate parent exists, as confirmed in Objective 1), state that explicitly and leave the parent contact fields null — do not fall back to reusing the brand-level email for this field.
            - Only report an email if you actually see it written in a search result or fetched page — never guess a likely-looking address from a domain pattern (e.g. do not assume info@parentcompany.com exists just because the domain does).

            OBJECTIVE 2 — BRAND-LEVEL CONTACT DETAILS (mandatory dedicated search):
            - Search specifically for "{req.brand} customer service contact", "{req.brand} contact us", "{req.brand} headquarters phone emails".
            - Locate the brand's official contact page URL, verified general/corporate email addresses, and a verified phone number.
            - Only report emails or a phone number if you actually see it written in a search result or fetched page — never guess a likely-looking address or number from a domain name pattern.

            OBJECTIVE 3 — DISTRIBUTORS (broad search, then mandatory enrichment per entity):
            1. Search comprehensively for distribution channels, including:
            - Official distributors / Authorized partners
            - Master distributors / Regional brokers
            - Commercial beverage/food/industrial wholesalers (depending on industry)
            - Distributor locator pages / "Where to buy" merchant portals
            - B2B supply channels handling the brand
            2. Prioritize information from the brand's official portals, regional business filings, and confirmed B2B supplier networks.
            3. MANDATORY ENRICHMENT STEP — for EACH distributor company you find, before moving to the next one, run additional searches to fill in:
            - Full street address (not just city/state if a precise address is findable)
            - City, state, country
            - A specific email address (not just "they have a contact form" — search "[company name] email", "[company name] sales contact", check their About/Contact page content directly)
            - A specific phone number
            - The source URL where each of these specific facts was found
            Do not report a distributor with only a name and homepage URL — that is an incomplete entry. Treat "I found the company" and "I found their contact details" as two separate steps, and do not skip the second one.
            4. For the `official` determination, you must be able to point to a specific piece of evidence (e.g., "listed on quakeroats.com/where-to-buy" or "named as authorized distributor on brand's partner page"). If you cannot point to such evidence, mark official = false and note in the source field why (e.g., "general wholesaler, not confirmed as authorized partner").
            5. Include both national broad-line corporate suppliers and localized regional trade wholesalers. If multiple entities are discovered, include all of them.
            6. Only if a genuinely diligent enrichment search still turns up nothing for a field, mark that specific field null — but the address, city, state, and at least one of email/phone should be populated for the large majority of distributors you report, since these are all commercial businesses with public contact info.

            Mapping Guidelines:
            - Set official = true if they are verified authorized commercial partners or primary regional tier-1 trade wholesalers.
            - Set official = false if they are general secondary market wholesalers.

            Confidence Guidelines:
            - 95–100: Listed directly on the brand's official channels.
            - 80–94: Confirmed via regional partner directory or authorized B2B wholesale platform.
            - 60–79: Reputable trade/beverage/industrial distributor website but unconfirmed by corporate headquarters.
            - Below 60: Weak circumstantial evidence.

            CRITICAL ACCURACY RULE: Never fabricate, infer, or "complete" an email or phone number. An email like info@brandname.com that you have not actually observed in a source is fabrication even if it looks plausible. If unverified, write "unknown".

            Write out your findings in clear, structured detail: parent company section, brand contact section, then a list of distributor profiles with whatever contact data was actually verified.
    """

    try:
        # Step 1: Grounded research with Google Search
        research_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=research_prompt,
            config=GenerateContentConfig(
                tools=[Tool(google_search=GoogleSearch())],
                temperature=0,
            ),
        )

        research_text = research_response.text
        if not research_text:
            raise HTTPException(
                status_code=500,
                detail="Gemini returned no research content."
            )

        # Step 2: Structure the research into the generic Output schema
        structuring_prompt = f"""
            Based on the research notes below, extract and structure the information into the required schema.

            Brand: {req.brand}
            Country: {req.country}

            Research notes:
            {research_text}

            Follow these rules:
            - Populate `parent_company`, `official_website`, `brand_contact_page`, `brand_email`, and `brand_phone` from Objective 1/2 of the notes. If the notes say the brand has no separate parent company, set parent_company to null and do not guess.
            - Map all identified regional wholesalers, national broad-line suppliers, or certified distributors into the `distributors` array (this is the correct field name in the schema — do not invent a different field name).
            - For each distributor, populate every field the research notes contain — address, city, state, country, email, phone — do not leave a field null if the research notes mention that information anywhere, even in passing.
            - The `source` field is mandatory whenever it's available in the notes: it should contain the specific URL or reference that supports the distributor's contact details and official status. A distributor entry with `source: null` and `official: true` is not acceptable — if no source is given, official must be false.
            - Do not drop a valid distributor entity just because their specific contact email/phone was unavailable after enrichment; map what is available and leave only the genuinely unfound sub-fields as null.
            - Never fabricate contact details, emails, phone numbers, or parent companies. If a value cannot be directly traced to something stated in the research notes, return null — do not infer or pattern-match a value.
            - Populate `parent_company_email` and `parent_company_email_type` from Objective 1B of the notes. If the brand has no separate parent company, or no contact email was found for the parent, both fields should be null.
            - `parent_company_email_type` must be one of: investor_relations, media_press, corporate_general, or unknown — use unknown only if an email was found but its purpose/department couldn't be determined from the notes.
            - Never fabricate a parent_company_email by guessing a domain pattern. If the notes don't contain a directly observed email, return null.
        """

        structured_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=structuring_prompt,
            config=GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Output,
                temperature=0,
            ),
        )

        if structured_response.parsed is None:
            raise HTTPException(
                status_code=500,
                detail="Gemini returned an invalid structured response."
            )

        return structured_response.parsed

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    

