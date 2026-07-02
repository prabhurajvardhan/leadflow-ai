from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.collectors.base import BaseCollector, CollectedLead
from app.collectors.openstreetmap.collector import OpenStreetMapCollector
from app.collectors.websites.collector import WebsiteCollector
from app.crawler.crawler import WebsiteCrawler
from app.ai.analyzer import AIAnalyzer
from app.outreach.service import OutreachService
from app.database.models import Lead, Job, LeadStatus
from app.database.repository.lead_repository import LeadRepository
from app.database.repository.job_repository import JobRepository
from app.core.logger import get_logger

logger = get_logger("pipeline")


class PipelineOrchestrator:
    """Orchestrates the lead intelligence pipeline.
    
    Coordinates the flow of data between collectors, crawlers,
    AI analyzers, and outreach systems.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.lead_repo = LeadRepository(session)
        self.job_repo = JobRepository(session)
        self.logger = logger
    
    async def run_full_pipeline(
        self,
        workspace_id: int,
        query: str,
        location: str = None,
        max_leads: int = 100
    ) -> Dict[str, Any]:
        """Run the full lead intelligence pipeline.
        
        Steps:
        1. Collect leads from data sources
        2. Remove duplicates
        3. Crawl websites
        4. Extract contact information
        5. Analyze with AI
        6. Score and qualify leads
        """
        self.logger.info(f"Starting full pipeline for workspace {workspace_id}")
        
        # Create job
        job = await self.job_repo.create(
            workspace_id=workspace_id,
            job_type="full_pipeline",
            params={"query": query, "location": location, "max_leads": max_leads}
        )
        
        try:
            # Step 1: Collect leads
            await self.job_repo.update_status(job.id, "running", progress=10)
            collected_leads = await self._collect_leads(query, location, max_leads)
            
            self.logger.info(f"Collected {len(collected_leads)} leads")
            
            # Step 2: Deduplicate and store leads
            await self.job_repo.update_status(job.id, "running", progress=30)
            stored_leads = await self._store_leads(workspace_id, collected_leads)
            
            self.logger.info(f"Stored {len(stored_leads)} unique leads")
            
            # Step 3: Crawl websites and enrich
            await self.job_repo.update_status(job.id, "running", progress=50)
            enriched_leads = await self._enrich_leads(stored_leads)
            
            # Step 4: AI Analysis
            await self.job_repo.update_status(job.id, "running", progress=70)
            analyzed_leads = await self._analyze_leads(enriched_leads)
            
            # Step 5: Generate outreach content
            await self.job_repo.update_status(job.id, "running", progress=90)
            await self._generate_outreach_content(analyzed_leads)
            
            # Complete job
            await self.job_repo.complete_job(job.id, {
                "total_leads": len(collected_leads),
                "stored_leads": len(stored_leads),
                "enriched_leads": len(enriched_leads),
                "analyzed_leads": len(analyzed_leads)
            })
            
            self.logger.info(f"Pipeline completed successfully")
            
            return {
                "job_id": job.id,
                "collected": len(collected_leads),
                "stored": len(stored_leads),
                "enriched": len(enriched_leads),
                "analyzed": len(analyzed_leads)
            }
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            await self.job_repo.fail_job(job.id, str(e))
            raise
    
    async def run_collection_only(
        self,
        workspace_id: int,
        query: str,
        location: str = None,
        max_leads: int = 100,
        source: str = "google_maps"
    ) -> Dict[str, Any]:
        """Run only the lead collection step."""
        self.logger.info(f"Running collection for workspace {workspace_id}")
        
        job = await self.job_repo.create(
            workspace_id=workspace_id,
            job_type="google_maps_search",
            params={"query": query, "location": location, "max_leads": max_leads}
        )
        
        try:
            await self.job_repo.start_job(job.id)
            
            collected_leads = await self._collect_leads(query, location, max_leads, source)
            stored_leads = await self._store_leads(workspace_id, collected_leads)
            
            await self.job_repo.complete_job(job.id, {
                "collected": len(collected_leads),
                "stored": len(stored_leads)
            })
            
            return {
                "job_id": job.id,
                "collected": len(collected_leads),
                "stored": len(stored_leads)
            }
            
        except Exception as e:
            self.logger.error(f"Collection failed: {e}")
            await self.job_repo.fail_job(job.id, str(e))
            raise
    
    async def run_enrichment(
        self,
        workspace_id: int,
        lead_ids: List[int] = None,
        status: str = LeadStatus.NEW.value
    ) -> Dict[str, Any]:
        """Enrich leads with website data and AI analysis."""
        self.logger.info(f"Running enrichment for workspace {workspace_id}")
        
        job = await self.job_repo.create(
            workspace_id=workspace_id,
            job_type="lead_enrichment",
            params={"lead_ids": lead_ids, "status": status}
        )
        
        try:
            await self.job_repo.start_job(job.id)
            
            # Get leads to enrich
            if lead_ids:
                leads = []
                for lid in lead_ids:
                    lead = await self.lead_repo.get_by_id(lid, workspace_id)
                    if lead:
                        leads.append(lead)
            else:
                leads, _ = await self.lead_repo.get_all(
                    workspace_id=workspace_id,
                    limit=100,
                    status=status
                )
            
            # Enrich leads
            enriched = await self._enrich_leads(leads)
            
            # Analyze leads
            analyzed = await self._analyze_leads(enriched)
            
            await self.job_repo.complete_job(job.id, {
                "enriched": len(enriched),
                "analyzed": len(analyzed)
            })
            
            return {
                "job_id": job.id,
                "enriched": len(enriched),
                "analyzed": len(analyzed)
            }
            
        except Exception as e:
            self.logger.error(f"Enrichment failed: {e}")
            await self.job_repo.fail_job(job.id, str(e))
            raise
    
    async def _collect_leads(
        self,
        query: str,
        location: str = None,
        max_leads: int = 100,
        source: str = "openstreetmap"
    ) -> List[CollectedLead]:
        """Collect leads from configured sources."""
        collector: BaseCollector
        
        if source == "openstreetmap":
            collector = OpenStreetMapCollector()
        elif source == "google_maps":
            collector = GoogleMapsCollector()
        else:
            collector = OpenStreetMapCollector()  # Default to OSM
        
        return await collector.collect(query, location=location, max_results=max_leads)
    
    async def _store_leads(
        self,
        workspace_id: int,
        collected_leads: List[CollectedLead]
    ) -> List[Lead]:
        """Store collected leads in the database."""
        stored_leads = []
        
        for collected in collected_leads:
            # Check for existing lead by domain
            if collected.domain:
                existing = await self.lead_repo.get_by_domain(collected.domain, workspace_id)
                if existing:
                    self.logger.debug(f"Skipping duplicate: {collected.domain}")
                    continue
            
            # Create new lead
            lead_data = collected.to_dict()
            lead_data.pop("source", None)  # Don't store source in lead
            
            lead = await self.lead_repo.create(
                workspace_id=workspace_id,
                source=collected.source,
                source_data=collected.source_data,
                **lead_data
            )
            stored_leads.append(lead)
        
        await self.session.commit()
        return stored_leads
    
    async def _enrich_leads(self, leads: List[Lead]) -> List[Lead]:
        """Enrich leads with website data."""
        enriched = []
        
        async with WebsiteCrawler() as crawler:
            for lead in leads:
                if not lead.domain:
                    continue
                
                try:
                    url = f"https://{lead.domain}"
                    result = await crawler.crawl(url)
                    
                    if result.success:
                        # Update lead with website data
                        await self.lead_repo.update(lead.id,
                            description=result.pages[0].meta_description if result.pages else None
                        )
                        
                        # Update or create website record
                        await self._update_website(lead, result)
                        
                        # Update contacts with extracted data
                        await self._update_contacts(lead, result)
                        
                        enriched.append(lead)
                    
                    # Rate limiting
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    self.logger.error(f"Failed to enrich lead {lead.id}: {e}")
        
        return enriched
    
    async def _update_website(self, lead: Lead, crawl_result) -> None:
        """Update website record from crawl results."""
        from app.database.models import Website
        
        # Find existing or create new
        website = lead.website
        
        if not website:
            website = Website(lead_id=lead.id)
            self.session.add(website)
        
        website.url = crawl_result.url
        if crawl_result.pages:
            page = crawl_result.pages[0]
            website.title = page.title
            website.description = page.meta_description
            website.meta_description = page.meta_description
            website.headers = page.headings or {}
        
        website.technologies = [t.name for t in crawl_result.technologies]
        website.page_count = crawl_result.total_pages
        website.crawl_status = "completed"
        website.last_crawled = datetime.utcnow()
        
        await self.session.flush()
    
    async def _update_contacts(self, lead: Lead, crawl_result) -> None:
        """Update contact records from extracted data."""
        from app.database.models import Contact
        
        # Add emails as contacts
        for email in crawl_result.emails[:5]:  # Limit to 5
            # Check if contact exists
            existing = next(
                (c for c in lead.contacts if c.email == email),
                None
            )
            
            if not existing:
                contact = Contact(
                    lead_id=lead.id,
                    email=email,
                    source="website_extraction",
                    is_verified=False
                )
                self.session.add(contact)
        
        # Add phone if available
        if crawl_result.phones:
            phone = list(crawl_result.phones)[0]
            if not lead.phone:
                lead.phone = phone
        
        # Add social links
        from app.database.models import SocialProfile
        for platform, url in crawl_result.social_links.items():
            existing = next(
                (s for s in lead.social_profiles if s.platform == platform),
                None
            )
            
            if not existing:
                profile = SocialProfile(
                    lead_id=lead.id,
                    platform=platform,
                    url=url
                )
                self.session.add(profile)
        
        await self.session.flush()
    
    async def _analyze_leads(self, leads: List[Lead]) -> List[Lead]:
        """Analyze leads with AI."""
        analyzer = AIAnalyzer()
        analyzed = []
        
        for lead in leads:
            try:
                # Build lead data for analysis
                lead_data = {
                    "company_name": lead.company_name,
                    "domain": lead.domain,
                    "description": lead.description,
                    "city": lead.city,
                    "state": lead.state,
                    "country": lead.country,
                    "phone": lead.phone,
                    "linkedin_url": lead.linkedin_url,
                    "technologies": lead.website.technologies if lead.website else []
                }
                
                # Run analysis
                analysis = await analyzer.analyze_lead(lead_data)
                
                # Update lead with analysis
                await self.lead_repo.update(lead.id,
                    ai_score=analysis.get("ai_score"),
                    quality_tier=analysis.get("quality_tier"),
                    status=LeadStatus.ANALYZED.value if analysis.get("ai_score", 0) > 40 else LeadStatus.NEW.value
                )
                
                # Store AI report
                await self._store_ai_report(lead, analysis)
                
                analyzed.append(lead)
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Failed to analyze lead {lead.id}: {e}")
        
        return analyzed
    
    async def _store_ai_report(self, lead: Lead, analysis: Dict[str, Any]) -> None:
        """Store AI analysis report."""
        from app.database.models import AIReport
        
        # Remove existing report
        if lead.ai_report:
            await self.session.delete(lead.ai_report)
        
        report = AIReport(
            lead_id=lead.id,
            summary=analysis.get("summary"),
            pain_points=analysis.get("pain_points", []),
            opportunities=analysis.get("opportunities", []),
            recommendations=analysis.get("recommendations", []),
            score_breakdown=analysis.get("score_breakdown", {}),
            quality_tier=analysis.get("quality_tier"),
            company_size_estimate=analysis.get("company_size_estimate"),
            industry=analysis.get("industry"),
            funding_stage=analysis.get("funding_stage"),
            personalization_hints=analysis.get("personalization_hints", {}),
            ai_provider=analysis.get("ai_provider"),
            ai_model=analysis.get("ai_model"),
            tokens_used=analysis.get("tokens_used")
        )
        
        self.session.add(report)
        await self.session.flush()
    
    async def _generate_outreach_content(self, leads: List[Lead]) -> None:
        """Generate personalized outreach content for leads."""
        analyzer = AIAnalyzer()
        
        for lead in leads:
            if lead.quality_tier not in ["A", "B"]:
                continue
            
            try:
                # Build lead data
                lead_data = {
                    "company_name": lead.company_name,
                    "domain": lead.domain,
                    "description": lead.description,
                    "contact_name": lead.contacts[0].first_name if lead.contacts else None,
                    "contact_title": lead.contacts[0].title if lead.contacts else None,
                    "pain_points": lead.ai_report.pain_points if lead.ai_report else [],
                    "opportunities": lead.ai_report.opportunities if lead.ai_report else [],
                    "personalization_hints": lead.ai_report.personalization_hints if lead.ai_report else {},
                    "company_size_estimate": lead.ai_report.company_size_estimate if lead.ai_report else None,
                    "industry": lead.ai_report.industry if lead.ai_report else None
                }
                
                # Generate email
                email_content = await analyzer.generate_email(lead_data, "initial")
                
                # Store generated content (could add a field or table for this)
                self.logger.info(f"Generated email for {lead.company_name}")
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Failed to generate content for lead {lead.id}: {e}")
