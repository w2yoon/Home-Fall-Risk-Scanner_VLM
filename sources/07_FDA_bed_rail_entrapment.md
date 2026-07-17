# Source: FDA — Adult Portable Bed Rail Safety

- Publisher: U.S. Food and Drug Administration (FDA), Medical Devices
- URLs:
  - https://www.fda.gov/medical-devices/adult-portable-bed-rail-safety/safety-concerns-about-adult-portable-bed-rails
  - https://www.fda.gov/medical-devices/adult-portable-bed-rail-safety/recommendations-consumers-and-caregivers-about-adult-portable-bed-rails
- License: U.S. federal government work — public domain
- Content current as of (per page): 02/27/2023
- Retrieved: 2026-07-17 (via browser fetch; direct WebFetch tool returned 404/403 on fda.gov and its cacmap.fda.gov mirror)
- **Why this file exists:** an earlier version of this project's knowledge base (`steadi_checklist.py`) recommended "Bed rail" as a missing-device item with no safety caveat and no verified source. Bed rails carry a documented, FDA-tracked entrapment/asphyxiation/death risk for certain populations. Any KB item recommending a bed rail must cite this file and include the high-risk-population caveat — recommending one unconditionally is the exact failure mode this project has already been corrected for once.

---

## Full text — Safety Concerns about Adult Portable Bed Rails

The Food and Drug Administration (FDA) and the U.S. Consumer Product Safety Commission (CPSC) have received death and injury reports related to adult portable bed rail products. Most of these reports were for entrapment, asphyxiation (suffocation), and falls. It is important to consider whether or not a bed rail product is appropriate when creating a safe sleeping environment that accounts for medical needs, comfort, and desire for freedom of movement.

### Risk of Entrapment

Entrapment can occur when a person is trapped by the bed rail in a position they cannot move from. This trapping can occur when the rail is not held securely against the mattress and the individual falls between the rail and the mattress, between the supports, within or under the rail.

People who want to be safe in bed should understand the risks associated with using bed rail products, take steps to ensure that they are installed and used correctly, and be aware that certain individuals should not use bed rails.

Adult portable bed rails should not be used as a restraint. They are intended to be assistive and should be used to facilitate mobility for those who need assistance getting in and out of bed or repositioning in bed.

Adult portable bed rails are not for everyone, nor every situation. Deaths and serious injuries can happen when using these products and devices. Even when adult portable bed rails are properly designed to reduce the risk of entrapment or falls, are compatible with the bed and mattress, and are used appropriately, they can present a hazard to certain individuals, particularly to people with physical limitations or altered mental status, such as dementia or delirium.

## Full text — Recommendations for Consumers and Caregivers about Adult Portable Bed Rails

Some people are at a high-risk for entrapment, falls or other injury from adult portable bed rails. High-risk people include those with pre-existing conditions such as confusion, restlessness, lack of muscle control, or a combination of these factors. Additionally, people who are cognitively impaired from the use of medication or from a medical condition, such as Alzheimer's or dementia, Parkinson's disease, Multiple Sclerosis (MS), balance disorders, stroke, or low blood pressure (hypotension), are at a higher risk of entrapment and injury.

Consider other alternatives when bed rails are not appropriate. Alternatives include roll guards, foam bumpers, lowering the bed as near to the floor as possible, using concave mattresses that can help reduce rolling off the bed, or a bed trapeze to help reposition while in bed and to get in and out of bed.

Adult portable bed rails should not be used as a substitute for proper monitoring, especially for people at high risk for entrapment and falls.

The FDA recommends the following actions to prevent deaths and injuries from entrapment and falls from adult portable bed rails:

**Before you install bed rails:**
- Check whether the adult portable bed rails you are using comply with ASTM F3186-17: Standard Specification for Adult Portable Bed Rails and Related Products. This FDA-recognized international consensus standard establishes performance criteria for adult portable bed rails including resistance to entrapment.
- Be aware that not all bed rails, mattresses, and bed frames are interchangeable and not all bed rails fit all size beds.
- Check with the manufacturers to make sure the bed rails, mattress, and bed frame are compatible, since most bed rails and mattresses are purchased separately from the bed frame.
- Rails should be selected and placed to discourage climbing over rails to get in and out of bed, which could lead to falls.

**When installing and using bed rails:**
- Confirm that the age, size, and weight of the person using the bed rails are appropriate for the bed rails used.
- Install bed rails using the manufacturer's instructions to ensure a proper fit.
- Ensure that the safety strap or bed rail retention system is permanently attached to the rail and secured to the bed frame according to the manufacturer's instructions.
- Regularly inspect the mattress and bed rails for gaps and areas of possible entrapment. Regardless of mattress width, length, and depth, the bed frame, bed rail and mattress should leave no gap wide enough to entrap a patient's head or body.
- Use caution when using bed rails with a soft mattress as this may increase risk of entrapment between the mattress and bed rail.
- Check bed rails regularly to make sure they are still installed correctly as rails may shift or loosen over time.

## Interpretation notes for KB authoring

- A bed-rail KB item must NOT be an unconditional "install a bed rail" recommendation. It must (a) name the entrapment risk, (b) note it is inappropriate for people with confusion, dementia, Parkinson's, MS, balance disorders, stroke, or hypotension, and (c) mention lower-risk alternatives (roll guards, foam bumpers, lowering the bed, bed trapeze) exist and that a clinician/OT should be involved in the choice.
- `action.image_treatment` for this item should be `"illustration"`, not `"composite"` or `"remove"` — this is exactly the kind of item Part 3.3 describes as requiring installation-correctness (gap width, strap attachment) that a photorealistic composite could get wrong in a way that looks authoritative and dangerous.
