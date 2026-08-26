export interface RightsCard {
  slug: string
  icon: string
  title: string
  situation: string
  rights: string[]
  whatToDo: string[]
  law: string
}

// Deliberately public, unauthenticated content (see App.tsx) — the point is spreading
// legal literacy to people who'll never register an account, not gating it. Each card
// is short enough to read and share in one sitting, e.g. on WhatsApp.
export const RIGHTS_CARDS: RightsCard[] = [
  {
    slug: 'police-stop-arrest',
    icon: '🚓',
    title: 'Stopped or arrested by police',
    situation: 'Police have stopped you, are questioning you, or are trying to arrest you.',
    rights: [
      'You have the right to know the grounds of arrest immediately.',
      'For offences carrying less than 7 years imprisonment, police must first issue a Section 41A notice to appear — arrest is not automatic (Arnesh Kumar v. State of Bihar, 2014).',
      'You must be produced before a magistrate within 24 hours of arrest.',
      'You have the right to inform a friend or relative of your arrest and its location.',
      'You have the right to consult a lawyer of your choice, including during interrogation.',
      'You cannot be forced to confess or sign blank papers.',
    ],
    whatToDo: [
      'Stay calm; do not resist physically even if you believe the arrest is unlawful.',
      'Ask clearly: "What is the reason for my arrest?"',
      'Ask to call a lawyer or family member — this is your right, not a favour.',
      'Note the officer\'s name, badge number, and the police station.',
      'Do not sign any document you have not read and understood.',
    ],
    law: 'Sections 41, 41A, 50, 57 of the Code of Criminal Procedure (CrPC); Article 22, Constitution of India',
  },
  {
    slug: 'tenant-rights',
    icon: '🏠',
    title: 'Landlord disputes as a tenant',
    situation: 'Your landlord is withholding your deposit, threatening eviction without notice, or entering without permission.',
    rights: [
      'A landlord generally cannot evict you without a court order or due notice, even if there is no written agreement.',
      'Your security deposit must be returned within a reasonable period after you vacate, minus any genuine deductions with proof.',
      'A landlord cannot cut off water/electricity to force you out — this can itself be a criminal offence.',
      'You are entitled to peaceful possession of the property for the agreed period.',
    ],
    whatToDo: [
      'Keep the rental agreement, rent receipts, and any WhatsApp/email communication as evidence.',
      'Send a written legal notice demanding the deposit or disputing the eviction.',
      'If utilities are cut off, this can be reported to police as illegal.',
      'Approach the Rent Controller or Civil Court if the landlord doesn\'t respond.',
    ],
    law: 'Transfer of Property Act, 1882; state-specific Rent Control Acts',
  },
  {
    slug: 'workplace-harassment',
    icon: '🏢',
    title: 'Sexual harassment at the workplace',
    situation: 'You are facing unwelcome sexual conduct, comments, or advances at work.',
    rights: [
      'Every employer with 10+ employees must have an Internal Complaints Committee (ICC).',
      'You can file a written complaint within 3 months of the incident (extendable).',
      'The enquiry must be completed within 90 days, and action taken within 60 days after that.',
      'You have the right to a copy of the complaint and enquiry report, and to confidentiality.',
      'Retaliation against you for complaining is itself punishable.',
    ],
    whatToDo: [
      'Write down what happened — dates, times, witnesses — as soon as possible.',
      'File a written complaint with your organisation\'s ICC.',
      'If there is no ICC, you can approach the Local Complaints Committee (LCC) at the district level.',
      'Preserve messages, emails, or CCTV-relevant timestamps as evidence.',
    ],
    law: 'Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013 (POSH Act)',
  },
  {
    slug: 'consumer-rights',
    icon: '🛒',
    title: 'A defective product or bad service',
    situation: 'A shop, seller, or service provider sold you something faulty or refuses a promised refund/repair.',
    rights: [
      'You have the right to a refund, replacement, or repair for defective goods or deficient services.',
      'You can claim compensation for any loss suffered because of the defect.',
      'E-commerce sellers are also covered — you don\'t need to have bought in person.',
      'Complaints can be filed without a lawyer, and filing fees are minimal.',
    ],
    whatToDo: [
      'Keep the invoice/receipt, product photos, and all communication with the seller.',
      'Send a written complaint to the seller first, giving a reasonable deadline to respond.',
      'If unresolved, file a complaint with the District Consumer Disputes Redressal Commission — claims up to ₹1 crore, or the National Commission for higher amounts.',
      'You can also complain on the National Consumer Helpline (1800-11-4000) or the INGRAM portal.',
    ],
    law: 'Consumer Protection Act, 2019',
  },
  {
    slug: 'domestic-violence',
    icon: '🛡️',
    title: 'Domestic violence or abuse at home',
    situation: 'You are facing physical, verbal, emotional, sexual, or economic abuse from a spouse or family member.',
    rights: [
      'You can seek a Protection Order preventing the abuser from contacting or approaching you.',
      'You have the right to continue residing in the shared household — you cannot simply be thrown out.',
      'You can claim monetary relief for medical expenses, loss of earnings, and maintenance.',
      'You can seek custody of your children.',
      'Complaints can be filed regardless of whether you are married to the abuser.',
    ],
    whatToDo: [
      'If you are in immediate danger, call 100 (police) or 181 (Women Helpline) first.',
      'Contact a Protection Officer at your local District Legal Services Authority — this is a free, government-appointed role that exists specifically to help you.',
      'You do not need a lawyer to file a Domestic Incident Report.',
      'Keep any medical records, photos, or messages that document the abuse.',
    ],
    law: 'Protection of Women from Domestic Violence Act, 2005',
  },
  {
    slug: 'cheque-bounce',
    icon: '💸',
    title: 'Someone\'s cheque to you has bounced',
    situation: 'A cheque you received for a payment has been dishonoured due to insufficient funds.',
    rights: [
      'A dishonoured cheque for a legally enforceable debt is a criminal offence, not just a civil matter.',
      'You can claim the cheque amount plus damages through both a criminal complaint and a civil recovery suit.',
      'The drawer can face imprisonment up to 2 years and/or a fine up to twice the cheque amount.',
    ],
    whatToDo: [
      'Get the bank\'s cheque-return memo confirming the reason for dishonour.',
      'Send a written legal notice demanding payment within 30 days of the dishonour memo.',
      'If unpaid after 15 days from the notice, you can file a criminal complaint within 1 month after that.',
      'Do not delay — these are strict, short deadlines.',
    ],
    law: 'Section 138, Negotiable Instruments Act, 1881',
  },
  {
    slug: 'right-to-information',
    icon: '📄',
    title: 'Getting information from a government office',
    situation: 'You want to know why a government decision was made, or get records a public authority is holding.',
    rights: [
      'Any citizen can request information from a public authority — no reason needs to be given.',
      'The authority must respond within 30 days (48 hours if it concerns life or liberty).',
      'The application fee is nominal (typically ₹10), and free for those below the poverty line.',
      'If refused or ignored, you have a right to appeal, first internally, then to the Information Commission.',
    ],
    whatToDo: [
      'Write a specific, clear request — vague requests are more easily refused.',
      'Address it to the Public Information Officer (PIO) of the relevant department.',
      'Keep proof of submission (receipt, registered post, or online acknowledgment).',
      'If there\'s no response in 30 days, that itself is grounds for a first appeal.',
    ],
    law: 'Right to Information Act, 2005',
  },
  {
    slug: 'wage-labour-rights',
    icon: '👷',
    title: 'Unpaid wages or unsafe working conditions',
    situation: 'An employer has not paid your wages, paid less than the minimum wage, or terminated you without due process.',
    rights: [
      'You are entitled to at least the minimum wage notified for your state and category of work.',
      'Wages must be paid on time — delay itself is a violation.',
      'Termination of a workman generally requires notice or compensation, and in larger establishments, government permission.',
      'You have the right to raise a dispute before the Labour Court without needing to hire a lawyer initially.',
    ],
    whatToDo: [
      'Keep any attendance records, payslips, or messages about your work and pay.',
      'Raise a written complaint with the employer first.',
      'File a complaint with the Labour Commissioner\'s office in your area — this is free.',
      'For unresolved disputes, the matter can be referred to a Labour Court or Industrial Tribunal.',
    ],
    law: 'Minimum Wages Act, 1948; Industrial Disputes Act, 1947; Payment of Wages Act, 1936',
  },
]
